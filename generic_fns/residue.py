###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007 Edward d'Auvergne                             #
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

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxFileEmptyError, RelaxNoPdbChainError, RelaxNoRunError, RelaxNoSequenceError, RelaxSequenceError, RelaxSpinSelectDisallowError
from selection import molecule_loop, parse_token, residue_loop, return_molecule, return_residue, return_single_residue_info, tokenise


def copy(pipe_from=None, res_from=None, pipe_to=None, res_to=None):
    """Copy the contents of the residue structure from one residue to a new residue.

    For copying to be successful, the res_from identification string must match an existent residue.
    The new residue number must be unique.

    @param pipe_from:   The data pipe to copy the residue from.  This defaults to the current data
                        pipe.
    @type pipe_from:    str
    @param res_from:    The residue identification string for the structure to copy the data from.
    @type res_from:     str
    @param pipe_to:     The data pipe to copy the residue to.  This defaults to the current data
                        pipe.
    @type pipe_to:      str
    @param res_to:      The residue identification string for the structure to copy the data to.
    @type res_to:       str
    """

    # The current data pipe.
    if pipe_from == None:
        pipe_from = relax_data_store.current_pipe
    if pipe_to == None:
        pipe_to = relax_data_store.current_pipe

    # The second pipe does not exist.
    if pipe_to not in relax_data_store.keys():
        raise RelaxNoRunError, pipe_to

    # Split up the selection string.
    mol_from_token, res_from_token, spin_from_token = tokenise(res_from)
    mol_to_token, res_to_token, spin_to_token = tokenise(res_to)

    # Disallow spin selections.
    if spin_from_token != None or spin_to_token != None:
        raise RelaxSpinSelectDisallowError

    # Parse the residue token for renaming and renumbering.
    res_num_to, res_name_to = return_single_residue_info(res_to_token)

    # Test if the residue number already exists.
    res_to_cont = return_residue(res_to, pipe_to)
    if res_to_cont:
        raise RelaxError, "The residue " + `res_to` + " already exists in the " + `pipe_from` + " data pipe."

    # Get the single residue data container.
    res_from_cont = return_residue(res_from, pipe_from)

    # No residue to copy data from.
    if res_from_cont == None:
        raise RelaxError, "The residue " + `res_from` + " does not exist in the " + `pipe_from` + " data pipe."

    # Get the single molecule data container to copy the residue to.
    mol_to_container = return_molecule(res_to, pipe_to)

    # Copy the data.
    if mol_to_container.res[0].num == None and mol_to_container.res[0].name == None and len(mol_to_container.res) == 1:
        mol_to_container.res[0] = res_from_cont.__clone__()
    else:
        mol_to_container.res.append(res_from_cont.__clone__())

    # Change the new residue number and name.
    if res_num_to != None:
        mol_to_container.res[-1].num = res_num_to
    if res_name_to != None:
        mol_to_container.res[-1].name = res_name_to


def create(res_num=None, res_name=None):
    """Function for adding a residue into the relax data store."""

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoRunError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if the residue number already exists.
    for i in xrange(len(cdp.mol[0].res)):
        if cdp.mol[0].res[i].num == res_num:
            raise RelaxError, "The residue number '" + `res_num` + "' already exists in the sequence."

    # If no residue data exists, replace the empty first residue with this residue.
    if cdp.mol[0].res[0].num == None and cdp.mol[0].res[0].name == None and len(cdp.mol[0].res) == 1:
        cdp.mol[0].res[0].num = res_num
        cdp.mol[0].res[0].name = res_name

    # Append the residue.
    else:
        cdp.mol[0].res.add_item(res_num=res_num, res_name=res_name)


def delete(res_id=None):
    """Function for deleting residues from the current data pipe.

    @param res_id:  The molecule and residue identifier string.
    @type res_id:   str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Parse the tokens.
    residues = parse_token(res_token)

    # Molecule loop.
    for mol in molecule_loop(mol_token):
        # List of indecies to delete.
        indecies = []

        # Loop over the residues of the molecule.
        for i in xrange(len(mol.res)):
            # Remove the residue is there is a match.
            if mol.res[i].num in residues or mol.res[i].name in residues:
                indecies.append(i)

        # Reverse the indecies.
        indecies.reverse()

        # Delete the residues.
        for index in indecies:
            mol.res.pop(index)

        # Create an empty residue container if no residues remain.
        if len(mol.res) == 0:
            mol.res.add_item()


def rename(res_id, new_name=None):
    """Function for renaming residues.

    @param res_id:      The identifier string for the residue(s) to rename.
    @type res_id:       str
    @param new_name:    The new residue name.
    @type new_name:     str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Parse the tokens.
    residues = parse_token(res_token)

    # Molecule loop.
    for mol in molecule_loop(mol_token):
        # Loop over the residues of the molecule.
        for i in xrange(len(mol.res)):
            # Rename the residue is there is a match.
            if mol.res[i].num in residues or mol.res[i].name in residues:
                mol.res[i].name = new_name


def renumber(res_id, new_number=None):
    """Function for renumbering residues.

    @param res_id:      The identifier string for the residue(s) to renumber.
    @type res_id:       str
    @param new_number:  The new residue number.
    @type new_number:   str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Parse the tokens.
    residues = parse_token(res_token)

    # Catch multiple renumberings!
    number = 0
    for mol in molecule_loop(mol_token):
        # Loop over the residues of the molecule.
        for i in xrange(len(mol.res)):
            # Rename the residue is there is a match.
            if mol.res[i].num in residues or mol.res[i].name in residues:
                number = number + 1

    # Fail if multiple residues are numbered.
    if number > 1:
        raise RelaxError, "The renumbering of multiple residues is disallowed."

    # Molecule loop.
    for mol in molecule_loop(mol_token):
        # Loop over the residues of the molecule.
        for i in xrange(len(mol.res)):
            # Rename the residue is there is a match.
            if mol.res[i].num in residues or mol.res[i].name in residues:
                mol.res[i].num = new_number


class Residue:
    def __init__(self, relax):
        """Class containing functions specific to amino-acid sequence."""

        self.relax = relax


    def data_names(self):
        """Function for returning a list of names of data structures associated with the sequence."""

        return [ 'res' ]


    def display(self, run=None):
        """Function for displaying the sequence."""

        # Test if the run exists.
        if not run in relax_data_store.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not relax_data_store.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Print a header.
        print "%-8s%-8s%-10s" % ("Number", "Name", "Selected")

        # Print the sequence.
        for i in xrange(len(relax_data_store.res[run])):
            print "%-8i%-8s%-10i" % (relax_data_store.res[run][i].num, relax_data_store.res[run][i].name, relax_data_store.res[run][i].select)


    def load_PDB_sequence(self, run=None):
        """Function for loading the sequence out of a PDB file.

        This needs to be modified to handle multiple peptide chains.
        """

        # Print out.
        print "\nLoading the sequence from the PDB file.\n"

        # Reassign the sequence of the first structure.
        if relax_data_store.pdb[run].structures[0].peptide_chains:
            res = relax_data_store.pdb[run].structures[0].peptide_chains[0].residues
            molecule = 'protein'
        elif relax_data_store.pdb[run].structures[0].nucleotide_chains:
            res = relax_data_store.pdb[run].structures[0].nucleotide_chains[0].residues
            molecule = 'nucleic acid'
        else:
            raise RelaxNoPdbChainError

        # Add the run to 'relax_data_store.res'.
        relax_data_store.res.add_list(run)

        # Loop over the sequence.
        for i in xrange(len(res)):
            # Append a data container.
            relax_data_store.res[run].add_item()

            # Residue number.
            relax_data_store.res[run][i].num = res[i].number

            # Residue name.
            if molecule == 'nucleic acid':
                relax_data_store.res[run][i].name = res[i].name[-1]
            else:
                relax_data_store.res[run][i].name = res[i].name

            # Select the residue.
            relax_data_store.res[run][i].select = 1


    def read(self, run=None, file=None, dir=None, num_col=0, name_col=1, sep=None):
        """Function for reading sequence data."""

        # Test if the run exists.
        if not run in relax_data_store.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data has already been read.
        if relax_data_store.res.has_key(run):
            raise RelaxSequenceError, run

        # Extract the data from the file.
        file_data = self.relax.IO.extract_data(file, dir)

        # Count the number of header lines.
        header_lines = 0
        for i in xrange(len(file_data)):
            try:
                int(file_data[i][num_col])
            except:
                header_lines = header_lines + 1
            else:
                break

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip data.
        file_data = self.relax.IO.strip(file_data)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxFileEmptyError

        # Test if the sequence data is valid.
        for i in xrange(len(file_data)):
            try:
                int(file_data[i][num_col])
            except ValueError:
                raise RelaxError, "Sequence data is invalid."

        # Add the run to 'relax_data_store.res'.
        relax_data_store.res.add_list(run)

        # Fill the array 'relax_data_store.res[run]' with data containers and place sequence data into the array.
        for i in xrange(len(file_data)):
            # Append a data container.
            relax_data_store.res[run].add_item()

            # Insert the data.
            relax_data_store.res[run][i].num = int(file_data[i][num_col])
            relax_data_store.res[run][i].name = file_data[i][name_col]
            relax_data_store.res[run][i].select = 1


    def sort(self, run=None):
        """Function for sorting the sequence by residue number."""

        # Test if the run exists.
        if not run in relax_data_store.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not relax_data_store.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Sort the sequence.
        relax_data_store.res[run].sort(self.sort_cmpfunc)


    def sort_cmpfunc(self, x, y):
        """Sequence comparison function given to the ListType function 'sort'."""

        if x.num > y.num:
            return 1
        elif x.num < y.num:
            return -1
        elif x.num == y.num:
            return 0


    def write(self, run=None, file=None, dir=None, force=0):
        """Function for writing sequence data."""

        # Test if the run exists.
        if not run in relax_data_store.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not relax_data_store.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Open the file for writing.
        seq_file = self.relax.IO.open_write_file(file, dir, force)

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[run])):
            # Residue number.
            seq_file.write("%-5i" % relax_data_store.res[run][i].num)

            # Residue name.
            seq_file.write("%-6s" % relax_data_store.res[run][i].name)

            # New line.
            seq_file.write("\n")

        # Close the results file.
        seq_file.close()
