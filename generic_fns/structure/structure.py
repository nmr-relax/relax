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
from math import sqrt, cos, pi, sin
from numpy import arccos, array, dot, eye, float64, zeros
from os import F_OK, access
from re import compile, match
from string import ascii_uppercase
from warnings import warn

# relax module imports.
from data import Data as relax_data_store
from generic_fns import molmol
from generic_fns.sequence import load_PDB_sequence
from generic_fns.selection import exists_mol_res_spin_data, return_molecule, return_residue, return_spin, spin_loop
from maths_fns.rotation_matrix import R_2vect
from physical_constants import ArH, ArC, ArN, ArO, ArS
from relax_errors import RelaxError, RelaxFileError, RelaxNoPdbChainError, RelaxNoPdbError, RelaxNoResError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoTensorError, RelaxNoVectorsError, RelaxPdbError, RelaxPdbLoadError, RelaxRegExpError
from relax_io import get_file_path, open_write_file
from relax_warnings import RelaxNoAtomWarning, RelaxNoPDBFileWarning, RelaxWarning, RelaxZeroVectorWarning



def centre_of_mass(return_mass=False):
    """Calculate and return the centre of mass of the structure.

    @param return_mass: A flag which if False will cause only the centre of mass to be returned, but
                        if True will cause the centre of mass and the mass itself to be returned as
                        a tuple.
    @type return_mass:  bool
    @return:            The centre of mass vector, and additionally the mass.
    @rtype:             list of 3 floats (or tuple of a list of 3 floats and one float)
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if a structure has been loaded.
    if not hasattr(cdp.structure, 'structures'):
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


def read_pdb(run=None, file=None, dir=None, model=None, load_seq=1, fail=1, verbosity=1):
    """The pdb loading function."""

    # Tests.
    ########

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if PDB data corresponding to the run already exists.
    if hasattr(cdp, 'struct'):
        raise RelaxPdbError

    # Test if sequence data is loaded.
    if not load_seq and not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # The file path.
    file_path = get_file_path(file, dir)

    # Test if the file exists.
    if not access(file_path, F_OK):
        if fail:
            raise RelaxFileError, ('PDB', file_path)
        else:
            warn(RelaxNoPDBFileWarning(file_path))
            return


    # Data creation.
    ################

    # File name.
    cdp.structure.file_name = file_path

    # Model.
    cdp.structure.model = model


    # Load the structures.
    ######################

    load_structures(file_path, model, verbosity)


    # Finish.
    #########

    # Sequence loading.
    if load_seq and not exists_mol_res_spin_data():
        load_PDB_sequence()

    # Load into Molmol (if running).
    molmol.open_pdb()


def set_vector(spin=None, xh_vect=None):
    """Place the XH unit vector into the spin container object.

    @keyword spin:      The spin container object.
    @type spin:         SpinContainer instance
    @keyword xh_vect:   The unit vector parallel to the XH bond.
    @type xh_vect:      array of len 3
    """

    # Place the XH unit vector into the container.
    spin.xh_vect = xh_vect


def vectors(heteronuc=None, proton=None, spin_id=None, verbosity=1):
    """Function for calculating/extracting the XH unit vector from the loaded structure.

    @param heteronuc:   The name of the heteronucleus.
    @type heteronuc:    str
    @param proton:      The name of the proton.
    @type proton:       str
    @param spin_id:     The molecule, residue, and spin identifier string.
    @type spin_id:      str
    @param verbosity:   The higher the value, the more information is printed to screen.
    @type verbosity:    int
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if the PDB file has been loaded.
    if not hasattr(cdp, 'structure'):
        raise RelaxPdbError

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test that the nuclei have been correctly set.
    if heteronuc == proton:
        raise RelaxError, "The proton and heteronucleus are set to the same atom."

    # Number of structures.
    num_str = len(cdp.structure.structures)

    # Print out.
    if verbosity:
        if num_str > 1:
            print "\nCalculating and averaging the unit XH vectors from all structures."
        else:
            print "\nCalculating the unit XH vectors from the structure."

    # Loop over the sequence.
    for spin in spin_loop(spin_id):
        # Skip unselected residues.
        if not spin.select:
            continue

        # Set the proton and heteronucleus names.
        spin.proton = proton
        spin.heteronuc = heteronuc

        # Calculate the vector.
        vector = xh_vector(spin)

        # Set the vector and deselect the spin if the vector doesn't exist.
        if vector != None:
            spin.xh_vect = vector    
        else:
            spin.select = False
