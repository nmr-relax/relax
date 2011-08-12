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

# Python module imports.
from numpy import float64, zeros
from warnings import warn

# relax module imports.
from generic_fns.mol_res_spin import return_molecule, return_residue, return_spin
from physical_constants import return_atomic_mass
from relax_errors import RelaxError, RelaxNoPdbError
from relax_warnings import RelaxWarning



def centre_of_mass(return_mass=False):
    """Calculate and return the centre of mass of the structure.

    @keyword return_mass:   A flag which if False will cause only the centre of mass to be returned,
                            but if True will cause the centre of mass and the mass itself to be
                            returned as a tuple.
    @type return_mass:      bool
    @return:                The centre of mass vector, and additionally the mass.
    @rtype:                 list of 3 floats (or tuple of a list of 3 floats and one float)
    """

    # Test if a structure has been loaded.
    if not hasattr(cdp, 'structure'):
        raise RelaxNoPdbError

    # Print out.
    print("Calculating the centre of mass.")

    # Initialise the centre of mass.
    R = zeros(3, float64)

    # Initialise the total mass.
    M = 0.0

    # Loop over all atoms.
    for mol_name, res_num, res_name, atom_num, atom_name, element, pos in cdp.structure.atom_loop(mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True):
        # Initialise the spin id string.
        id = ''

        # Get the corresponding molecule container.
        if mol_name == None:
            mol_cont = cdp.mol[0]
        else:
            id = id + '#' + mol_name
            mol_cont = return_molecule(id)

        # Get the corresponding residue container.
        if res_name == None and res_num == None:
            res_cont = mol_cont.res[0]
        else:
            id = id + ':' + repr(res_num)
            res_cont = return_residue(id)

        # Get the corresponding spin container.
        if atom_name == None and atom_num == None:
            spin_cont = res_cont.spin[0]
        else:
            id = id + '@' + repr(atom_num)
            spin_cont = return_spin(id)

        # Deselected spins.
        if spin_cont and not spin_cont.select:
            continue

        # No element?
        if element == None:
            warn(RelaxWarning("Skipping the atom '%s' as the element type cannot be determined." % id))
            continue

        # Atomic mass.
        try:
            mass = return_atomic_mass(element)
        except RelaxError:
            warn(RelaxWarning("Skipping the atom '%s' as the element '%s' is unknown." % (id, element)))

        # Total mass.
        M = M + mass

        # Sum of mass * position.
        R = R + mass * pos

    # Normalise.
    R = R / M

    # Final print out.
    print(("    Total mass:      M = " + repr(M)))
    print(("    Centre of mass:  R = " + repr(R)))

    # Return the centre of mass.
    if return_mass:
        return R, M
    else:
        return R
