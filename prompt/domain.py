###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Module containing the 'domain' user function for defining structural domains."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import Basic_class, _build_doc
import arg_check
from generic_fns import domain
from relax_errors import RelaxListStrError, RelaxNoneStrListError, RelaxNoneTupleError
from specific_fns.model_free import Model_free


class Domain(Basic_class):
    """Class containing the user function for defining domains."""

    def domain(self, id=None, spin_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "domain("
            text = text + "id=" + repr(id)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(id, 'domain ID string')
        arg_check.is_str(spin_id, 'spin ID string', can_be_none=True)

        # Execute the functional code.
        domain.define(id=id, spin_id=spin_id)

    # The function doc info.
    domain._doc_title = "Definition of structural domains."
    domain._doc_title_short = "Domain definition."
    domain._doc_args = [
        ["id", "The domain ID string."],
        ["spin_id", "The spin ID string of all atomic members of the domain."]
    ]
    domain._doc_desc = """
        This is used to define structural domains.  Multiple domains can be defined, and these can overlap.  Rather than labelling the currently loaded spins with the ID string, the spin ID string is stored for later use.  This allows new spins to be loaded later and still be included within the same domain.
        """
    _build_doc(domain)
