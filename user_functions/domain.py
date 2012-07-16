###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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

# Module docstring.
"""The domain user function definitions."""

# relax module imports.
from generic_fns import domain
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The domain user function.
uf = uf_info.add_uf('domain')
uf.title = "Definition of structural domains."
uf.title_short = "Domain definition."
uf.add_keyarg(
    name = "id",
    py_type = "str",
    desc_short = "domain ID string",
    desc = "The ID string used to identify molecular domains.",
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "spin ID string",
    desc = "The spin ID string of all atomic members of the domain.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is used to define structural domains.  Multiple domains can be defined, and these can overlap.  Rather than labelling the currently loaded spins with the ID string, the spin ID string is stored for later use.  This allows new spins to be loaded later and still be included within the same domain.")
uf.backend = domain.define
uf.menu_text = "&domain"
