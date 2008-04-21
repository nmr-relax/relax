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
from math import sqrt
from numpy import dot, ndarray
from os import F_OK, access
import sys
from warnings import warn

# relax module imports.
from data import Data as relax_data_store
from generic_fns import molmol
from generic_fns.selection import exists_mol_res_spin_data, generate_spin_id, return_molecule, return_residue, return_spin, spin_loop
from generic_fns.sequence import write_header, write_line
from generic_fns.structure.scientific import Scientific_data
from relax_errors import RelaxError, RelaxFileError, RelaxNoPipeError, RelaxNoSequenceError, RelaxPdbError
from relax_io import get_file_path
from relax_warnings import RelaxNoPDBFileWarning, RelaxZeroVectorWarning



def load_spins(spin_id=None):
    """Load the spins from the structural object into the relax data store.

    @keyword spin_id:   The molecule, residue, and spin identifier string.
    @type spin_id:      str
    """

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Print out.
    print "Adding the following spins to the relax data store.\n"
    write_header(sys.stdout, mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True)

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Loop over all atoms of the spin_id selection.
    for mol_name, res_num, res_name, atom_num, atom_name, element, pos in cdp.structure.atom_loop(atom_id=spin_id, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True):
        # Initialise the identification string.
        id = ''

        # Get the molecule container corresponding to the molecule name.
        if mol_name:
            # Update the ID string.
            id = id + '#' + mol_name

            # The container.
            mol_cont = return_molecule(id)

        # The is only one molecule and it is unnamed.
        elif cdp.mol[0].name == None and len(cdp.mol) == 1:
            mol_cont = cdp.mol[0]

        # Add the molecule if it doesn't exist.
        if mol_name and mol_cont == None:
            # Add the molecule.
            cdp.mol.add_item(mol_name=mol_name)

            # Get the container.
            mol_cont = cdp.mol[-1]

        # Add the residue number to the ID string (residue name is ignored because only the number is unique).
        id = id + ':' + `res_num`

        # Get the corresponding residue container.
        res_cont = return_residue(id)

        # Add the residue if it doesn't exist.
        if res_num and res_name and res_cont == None:
            # Add the residue.
            mol_cont.res.add_item(res_name=res_name, res_num=res_num)

            # Get the container.
            res_cont = mol_cont.res[-1]

        # Add the atom number to the ID string (atom name is ignored because only the number is unique).
        id = id + '@' + `atom_num`

        # Get the corresponding spin container.
        spin_cont = return_spin(id)

        # Add the spin if it doesn't exist.
        if atom_name and spin_cont == None:
            # Add the spin.
            res_cont.spin.add_item(spin_name=atom_name, spin_num=atom_num)

            # Get the container.
            spin_cont = res_cont.spin[-1]

            # Print out when a spin is appended.
            write_line(sys.stdout, mol_name, res_num, res_name, atom_num, atom_name, mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True)

        # Add the position vector and element type to the spin container.
        spin_cont.pos = pos
        spin_cont.element = element


def read_pdb(file=None, dir=None, model=None, parser='scientific', fail=True, verbosity=1):
    """The PDB loading function.

    Parsers
    =======

    Currently only the Scientific Python parser is available for reading PDB files.  This parser is
    selected only if the parser keyword argument is set to 'scientific'.


    @keyword file:          The name of the PDB file to read.
    @type file:             str
    @keyword dir:           The directory where the PDB file is located.  If set to None, then the
                            file will be searched for in the current directory.
    @type dir:              str or None
    @keyword model:         The PDB model to extract from the file.  If set to None, then all models
                            will be loaded.
    @type model:            int or None
    @keyword parser:        The parser to be used to read the PDB file.
    @type parser:           str
    @keyword fail:          A flag which, if True, will cause a RelaxError to be raised if the PDB
                            file does not exist.  If False, then a RelaxWarning will be trown
                            instead.
    @type fail:             bool
    @keyword verbosity:     The amount of information to print to screen.  Zero corresponds to
                            minimal output while higher values increase the amount of output.  The
                            default value is 1.
    @type verbosity:        int
    @raise RelaxFileError:  If the fail flag is set, then a RelaxError is raised if the PDB file
                            does not exist.
    """

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if structural data already exists.
    if hasattr(cdp, 'struct'):
        raise RelaxPdbError

    # The file path.
    file_path = get_file_path(file, dir)

    # Test if the file exists.
    if not access(file_path, F_OK):
        if fail:
            raise RelaxFileError, ('PDB', file_path)
        else:
            warn(RelaxNoPDBFileWarning(file_path))
            return

    # Place the Scientific Python structural object into the relax data store.
    if parser == 'scientific':
        cdp.structure = Scientific_data()

    # Load the structures.
    cdp.structure.load_structures(file_path, model, verbosity)

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


def vectors(proton=None, spin_id=None, verbosity=1, unit=True):
    """Function for calculating/extracting the XH unit vector from the loaded structure.

    @param proton:      The name of the proton attached to the spin, as given in the structural
                        file.
    @type proton:       str
    @param spin_id:     The molecule, residue, and spin identifier string.
    @type spin_id:      str
    @param verbosity:   The higher the value, the more information is printed to screen.
    @type verbosity:    int
    @keyword unit:      A flag which if set will cause the function to return the unit XH vector
                        rather than the full vector.
    @type unit:         bool
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if the PDB file has been loaded.
    if not hasattr(cdp, 'structure'):
        raise RelaxPdbError

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Print out.
    if verbosity:
        if cdp.structure.num_models() > 1:
            print "\nCalculating and averaging the unit XH vectors from all structures."
        else:
            print "\nCalculating the unit XH vectors from the structure."

    # Header print out.
    write_header(sys.stdout, mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True)

    # Loop over the spins.
    for spin, mol_name, res_num, res_name in spin_loop(selection=spin_id, full_info=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # The spin identification string.
        spin_id = generate_spin_id(mol_name, res_num, res_name, spin.num, spin.name)

        # The XH vector already exists.
        if hasattr(spin, 'xh_vect'):
            warn(RelaxWarning("The XH vector for the spin " + `spin_id` + " already exists"))
            continue

        # Get the attached proton info.
        bonded_num, bonded_name, bonded_element, bonded_pos = cdp.structure.attached_atom(atom_id=spin_id, attached_atom=proton)

        # No attached proton.
        if (bonded_num, bonded_name, bonded_element, bonded_pos) == (None, None, None, None):
            continue

        # Convert the bonded_pos into a list if only a single model is being used.
        if type(bonded_pos) == ndarray:
            bonded_pos = [bonded_pos]

        # Print out.
        print bonded_num, bonded_name, bonded_element, bonded_pos






    # Loop over all the structural data.
    first_model = None
    spin_list = []
    for atom in cdp.structure.atom_loop(atom_id=spin_id, model_num_flag=True, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True):
        # Unpack the data.
        model_num, mol_name, res_num, res_name, atom_num, atom_name, element, pos = atom

        # The spin identification string.
        spin_id = generate_spin_id(mol_name, res_num, res_name, atom_num, atom_name)

        # Get the corresponding spin.
        spin = return_spin(selection=spin_id)

        # Proton name does not match, so skip the atom.
        if proton != atom_name:
            continue

        # No matching spin, so skip the atom.
        if not spin:
            continue

        # Skip deselected spins.
        if not spin.select:
            continue

        # The first model.
        if first_model == None:
            first_model = model_num

        # The XH vector already exists.
        if first_model == model_num and hasattr(spin, 'xh_vect'):
            warn(RelaxWarning("The XH vector for the spin " + `spin_id` + " already exists"))
            continue

        # Store the spin_id.
        if first_model == model_num:
            spin_list.append(spin_id)

        # Set the attached proton name.
        if not hasattr(spin, 'attached_proton'):
            spin.attached_proton = proton
        elif spin.attached_proton != proton:
            raise RelaxError, "The attached proton " + `spin.attached_proton` + " does not match the proton argument " + `proton` + "."

        # Set the heteronucleus and proton positions.
        posX = spin.pos
        posH = pos

        # Calculate the XH bond vector.
        vector = posH - posX

        # Unit vector.
        if unit:
            # Normalisation factor.
            norm_factor = sqrt(dot(vector, vector))

            # Test for zero length.
            if norm_factor == 0.0:
                warn(RelaxZeroVectorWarning(spin_id))

            # Calculate the normalised vector.
            else:
                vector = vector / norm_factor

        # Set the vector and deselect the spin if the vector doesn't exist.
        if not hasattr(spin, 'xh_vect'):
            spin.xh_vect = vector
        else:
            spin.xh_vect = spin.xh_vect + vector

    # Loop over all the modified spins.
    for spin_id in spin_list:
        # Get the spin.
        mol_name, res_num, res_name, spin = return_spin(selection=spin_id, full_info=True)

        # Print out of modified spins.
        write_line(sys.stdout, mol_name, res_num, res_name, atom_num, atom_name, mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True)

        # Average the XH vectors for all models.
        spin.xh_vect = spin.xh_vect / cdp.structure.num_models()
