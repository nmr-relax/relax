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
from os import F_OK, access
from warnings import warn

# relax module imports.
from data import Data as relax_data_store
from generic_fns import molmol
from generic_fns.sequence import load_PDB_sequence
from generic_fns.selection import exists_mol_res_spin_data, spin_loop
from generic_fns.structure.scientific import Scientific_data
from relax_errors import RelaxError, RelaxFileError, RelaxNoPipeError, RelaxNoSequenceError, RelaxPdbError
from relax_io import get_file_path
from relax_warnings import RelaxNoPDBFileWarning



def load_spins(spin_id=None):
    """Load the spins from the structural object into the relax data store.

    @keyword spin_id:   The molecule, residue, and spin identifier string.
    @type spin_id:      str
    """

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Print out.
    print "Generating the spins from the loaded structure.\n"

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Reassign the sequence of the first structure.
    if cdp.structure.structures[0].peptide_chains:
        chains = cdp.structure.structures[0].peptide_chains
        molecule = 'protein'
    elif cdp.structure.structures[0].nucleotide_chains:
        chains = cdp.structure.structures[0].nucleotide_chains
        molecule = 'nucleic acid'
    else:
        raise RelaxNoPdbChainError

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(spin_id)

    # Parse the tokens.
    molecules = parse_token(mol_token)
    residues = parse_token(res_token)
    spins = parse_token(spin_token)

    # Init some indecies.
    mol_index = 0
    res_index = 0
    spin_index = 0

    # Loop over the molecules.
    for chain in chains:
        # The name of the molecule.
        if chain.chain_id:
            mol_name = chain.chain_id
        elif chain.segment_id:
            mol_name = chain.segment_id
        else:
            mol_name = None

        # Skip non-matching molecules.
        if mol_token and mol_name not in molecules:
            continue

        # Add the molecule if there is a molecule name (otherwise everything goes into the default first MolecularContainer).
        if mol_name:
            # Replace the first empty molecule.
            if mol_index == 0 and cdp.mol[0].name == None:
                cdp.mol[0].name = mol_name

            # Create a new molecule.
            else:
                # Add the molecule.
                cdp.mol.add_item(mol_name=mol_name)

        # Loop over the residues.
        for res in chain.residues:
            # The residue name and number.
            if molecule == 'nucleic acid':
                res_name = res.name[-1]
            else:
                res_name = res.name
            res_num = res.number

            # Skip non-matching residues.
            if res_token and not (res_name in residues or res_num in residues):
                continue

            # Replace the first empty residue.
            if res_index == 0 and cdp.mol[mol_index].res[0].name == None:
                cdp.mol[mol_index].res[0].name = res_name
                cdp.mol[mol_index].res[0].num = res_num

            # Create a new residue.
            else:
                # Add the residue.
                cdp.mol[mol_index].res.add_item(res_name=res_name, res_num=res_num)

            # Loop over the spins.
            for atom in res.atom_list:
                # The spin name and number.
                spin_name = atom.name
                spin_num = atom.properties['serial_number']

                # Skip non-matching spins.
                if spin_token and not (spin_name in spins or spin_num in spins):
                    continue

                # Replace the first empty residue.
                if spin_index == 0 and cdp.mol[mol_index].res[res_index].spin[0].name == None:
                    cdp.mol[mol_index].res[res_index].spin[0].name = spin_name
                    cdp.mol[mol_index].res[res_index].spin[0].num = spin_num

                # Create a new residue.
                else:
                    # Add the residue.
                    cdp.mol[mol_index].res[res_index].spin.add_item(spin_name=spin_name, spin_num=spin_num)

                # Increment the residue index.
                spin_index = spin_index + 1

            # Increment the residue index.
            res_index = res_index + 1

        # Increment the molecule index.
        mol_index = mol_index + 1


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
