###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007-2008 Edward d'Auvergne                        #
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
"""Module for holding certain model components fixed during optimisation."""

# Python module imports.
from re import match

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import exists_mol_res_spin_data, spin_loop
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoTensorError


def fix(element, fixed):
    """Fix or allow certain model components values to vary during optimisation.

    @param element:     The model component to fix or unfix.  If set to 'diff', then the diffusion
                        parameters can be toggled.  If set to 'all_spins', then all spins can be
                        toggled.  If set to 'all', then all model components are toggled.
    @type element:      str.
    """

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = ds[ds.current_pipe]

    # Diffusion tensor.
    if element == 'diff' or element == 'all':
        # Test if the diffusion tensor data is loaded.
        if not hasattr(cdp, 'diff_tensor'):
            raise RelaxNoTensorError, 'diffusion'

        # Set the fixed flag.
        cdp.diff_tensor.fixed = fixed


    # All spins.
    elif element == 'all_spins' or element == 'all':
        # Test if sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over the sequence and set the fixed flag.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Set the flag.
            spin.fixed = fixed


    # Unknown.
    if element not in ['diff', 'all_spins', 'all']:
        raise RelaxError, "The 'element' argument " + `element` + " is unknown."
