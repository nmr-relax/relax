###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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

# relax module imports.
from data import Data as relax_data_store
from generic_fns.selection import return_molecule, return_residue, return_spin
from physical_constants import return_atomic_mass
from relax_errors import RelaxNoPdbError



def centre_of_mass(return_mass=False):
    """Calculate and return the centre of mass of the structure.

    @keyword return_mass:   A flag which if False will cause only the centre of mass to be returned,
                            but if True will cause the centre of mass and the mass itself to be
                            returned as a tuple.
    @type return_mass:      bool
    @return:                The centre of mass vector, and additionally the mass.
    @rtype:                 list of 3 floats (or tuple of a list of 3 floats and one float)
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if a structure has been loaded.
    if not hasattr(cdp, 'structure'):
        raise RelaxNoPdbError

    # Print out.
    print "Calculating the centre of mass."

    # Initialise the centre of mass.
    R = zeros(3, float64)

    # Initialise the total mass.
    M = 0.0

    # Loop over the structures.
    for struct in cdp.structure.structures:
        # Get the corresponding molecule container.
        if cdp.mol[0].name == None:
            mol_cont = cdp.mol[0]
        else:
            mol_cont = return_molecule('#' + struct.name)

        # Deselected molecule.
        if not mol_cont.select:
            continue

        # Protein.
        if struct.peptide_chains:
            chains = struct.peptide_chains

        # RNA/DNA.
        elif struct.nucleotide_chains:
            chains = struct.nucleotide_chains

        # Loop over the residues of the protein in the PDB file.
        for res in chains[0].residues:
            # Get the corresponding residue container.
            if mol_cont.res[0].name == None and mol_cont.res[0].num == None:
                res_cont = mol_cont.res[0]
            else:
                res_cont = return_residue(':' + `res.number`)

            # Deselected residue.
            if not res_cont.select:
                continue

            # Loop over the atoms of the residue.
            for atom in res:
                # Get the corresponding spin container.
                if res_cont.spin[0].name == None and res_cont.spin[0].num == None:
                    spin_cont = res_cont.spin[0]
                else:
                    spin_cont = return_spin('@' + `atom.properties['serial_number']`)

                # Deselected spin.
                if not spin_cont.select:
                    continue

                # Atomic mass.
                mass = return_atomic_mass(atom.properties['element'])

                # Total mass.
                M = M + mass

                # Sum of mass * position.
                R = R + mass * atom.position.array

    # Normalise.
    R = R / M

    # Final print out.
    print "    Total mass:      M = " + `M`
    print "    Centre of mass:  R = " + `R`

    # Return the centre of mass.
    if return_mass:
        return R,M
    else:
        return R
