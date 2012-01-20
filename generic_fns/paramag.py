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
"""Module for the manipulation of paramagnetic data."""

# Python module imports.
from math import sqrt
from numpy import array, float64, zeros
import sys
from warnings import warn

# relax module imports.
from generic_fns import grace, pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from relax_errors import RelaxError, RelaxNoPdbError, RelaxNoSequenceError, RelaxNoSpinError
from relax_io import open_write_file, read_spin_data, write_spin_data
from relax_warnings import RelaxWarning


def centre(pos=None, atom_id=None, pipe=None, verbosity=1, fix=True, ave_pos=False, force=False):
    """Specify the atom in the loaded structure corresponding to the paramagnetic centre.

    @keyword pos:       The atomic position.  If set, the atom_id string will be ignored.
    @type pos:          list of float
    @keyword atom_id:   The atom identification string.
    @type atom_id:      str
    @keyword pipe:      An alternative data pipe to extract the paramagnetic centre from.
    @type pipe:         None or str
    @keyword verbosity: The amount of information to print out.  The bigger the number, the more information.
    @type verbosity:    int
    @keyword fix:       A flag which if False causes the paramagnetic centre to be optimised during minimisation.
    @type fix:          bool
    @keyword ave_pos:   A flag which if True causes the atomic positions from multiple models to be averaged.
    @type ave_pos:      bool
    @keyword force:     A flag which if True will cause the current paramagnetic centre to be overwritten.
    @type force:        bool
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipes.
    source_dp = pipes.get_pipe(pipe)

    # Test if the structure has been loaded.
    if not hasattr(source_dp, 'structure'):
        raise RelaxNoPdbError

    # Test the centre has already been set.
    if pos != None and not force and hasattr(cdp, 'paramagnetic_centre'):
        raise RelaxError("The paramagnetic centre has already been set to the coordinates " + repr(cdp.paramagnetic_centre) + ".")

    # The fixed flag.
    if fix:
        print("The paramagnetic centre will be fixed during optimisation.")
    else:
        print("The paramagnetic centre will be optimised.")
    cdp.paramag_centre_fixed = fix

    # Position is supplied.
    if pos != None:
        centre = array(pos)
        num_pos = 1
        full_pos_list = []

    # Position from a loaded structure.
    elif atom_id:
        # Get the positions.
        centre = zeros(3, float64)
        full_pos_list = []
        num_pos = 0
        for spin, spin_id in spin_loop(atom_id, pipe=pipe, return_id=True):
            # No atomic positions.
            if not hasattr(spin, 'pos'):
                continue
    
            # Spin position list.
            if isinstance(spin.pos[0], float) or isinstance(spin.pos[0], float64):
                pos_list = [spin.pos]
            else:
                pos_list = spin.pos
    
            # Loop over the model positions.
            for pos in pos_list:
                full_pos_list.append(pos)
                centre = centre + array(pos)
                num_pos = num_pos + 1
    
        # No positional information!
        if not num_pos:
            raise RelaxError("No positional information could be found for the spin '%s'." % atom_id)

    # No position - so simply exit the function.
    else:
        return

    # Averaging.
    centre = centre / float(num_pos)

    # Print out.
    if verbosity:
        print("Paramagnetic centres located at:")
        for pos in full_pos_list:
            print(("    [%8.3f, %8.3f, %8.3f]" % (pos[0], pos[1], pos[2])))
        print("\nAverage paramagnetic centre located at:")
        print(("    [%8.3f, %8.3f, %8.3f]" % (centre[0], centre[1], centre[2])))

    # Set the centre (place it into the current data pipe).
    if ave_pos:
        if verbosity:
            print("\nUsing the average paramagnetic position.")
        cdp.paramagnetic_centre = centre
    else:
        if verbosity:
            print("\nUsing all paramagnetic positions.")
        cdp.paramagnetic_centre = full_pos_list
