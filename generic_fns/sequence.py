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
from relax_errors import RelaxError, RelaxFileEmptyError, RelaxNoPdbChainError, RelaxNoPipeError, RelaxNoSequenceError, RelaxSequenceError
from relax_io import extract_data, strip



def read(file=None, dir=None, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, sep=None):
    """Function for reading molecule, residue, and/or spin sequence data.

    @param file:            The name of the file to open.
    @type file:             str
    @param dir:             The directory containing the file (defaults to the current directory if
                            None).
    @type dir:              str or None
    @param mol_name_col:    The column containing the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column containing the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column containing the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column containing the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column containing the spin number information.
    @type spin_num_col:     int or None
    @param sep:             The column seperator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # Test if sequence data already exists.
    if sequence_exists():
        raise RelaxSequenceError

    # Extract the data from the file.
    file_data = extract_data(file, dir)

    # Count the number of header lines.
    header_lines = 0
    for i in xrange(len(file_data)):
        # Residue number.
        if res_num_col != None:
            try:
                int(file_data[i][res_num_col])
            except ValueError:
                header_lines = header_lines + 1
            else:
                break

        # Spin number.
        elif spin_num_col != None:
            try:
                int(file_data[i][spin_num_col])
            except ValueError:
                header_lines = header_lines + 1
            else:
                break

    # Remove the header.
    file_data = file_data[header_lines:]

    # Strip data.
    file_data = strip(file_data)

    # Do nothing if the file does not exist.
    if not file_data:
        raise RelaxFileEmptyError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if the sequence data is valid.
    validate_sequence(file_data, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col)

    # Init some indecies.
    mol_index = 0
    res_index = 0

    # Fill the molecule-residue-spin data.
    for i in xrange(len(file_data)):
        # A new molecule.
        if mol_name_col and cdp.mol[mol_index].name != file_data[i][mol_name_col]:
            # Create a new molecule.
            cdp.mol.add_item(mol_name=file_data[i][mol_name_col])

            # Increment the molecule index.
            mol_index = mol_index + 1

        # A new residue.
        if res_name_col and cdp.mol[mol_index].res[res_index].name != file_data[i][res_name_col]:
            # Create a new residue.
            cdp.mol[mol_index].res.add_item(res_name=file_data[i][res_name_col], res_num=int(file_data[i][res_num_col]))

            # Increment the residue index.
            res_index = res_index + 1

        # A new spin.
        if spin_num_col:
            cdp.mol[mol_index].res[res_index].spin.add_item(spin_name=file_data[i][spin_name_col], spin_num=int(file_data[i][spin_num_col]))


def sequence_exists():
    """Function for determining if sequence data already exists in the current data pipe.

    @return:    The answer to the question.
    @rtype:     Boolean
    """

    # Dummy return
    return False


def validate_sequence(data, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None):
    """Function for testing if the sequence data is valid.

    The only function this performs is to raise a RelaxError if the data is invalid.


    @param data:            The sequence data.
    @type data:             list of lists.
    @param mol_name_col:    The column containing the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column containing the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column containing the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column containing the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column containing the spin number information.
    @type spin_num_col:     int or None
    """

    # Loop over the data.
    for i in xrange(len(data)):
        # Molecule name data.
        if mol_name_col != None:
            try:
                data[i][mol_name_col]
            except IndexError:
                raise RelaxInvalidSeqError, data[i]

        # Residue number data.
        if res_num_col != None:
            # No data in column.
            try:
                data[i][res_num_col]
            except IndexError:
                raise RelaxInvalidSeqError, data[i]

            # Bad data in column.
            try:
                int(data[i][res_num_col])
            except ValueError:
                raise RelaxInvalidSeqError, data[i]

        # Residue name data.
        if res_name_col != None:
            try:
                data[i][res_name_col]
            except IndexError:
                raise RelaxInvalidSeqError, data[i]

        # Spin number data.
        if spin_num_col != None:
            # No data in column.
            try:
                data[i][spin_num_col]
            except IndexError:
                raise RelaxInvalidSeqError, data[i]

            # Bad data in column.
            try:
                int(data[i][spin_num_col])
            except ValueError:
                raise RelaxInvalidSeqError, data[i]

        # Spin name data.
        if spin_name_col != None:
            try:
                data[i][spin_name_col]
            except IndexError:
                raise RelaxInvalidSeqError, data[i]




class Sequence:
    def __init__(self, relax):
        """Class containing functions specific to amino-acid sequence."""

        self.relax = relax


    def add(self, run=None, res_num=None, res_name=None, select=1):
        """Function for adding a residue onto the sequence."""

        # Test if the run exists.
        if not run in relax_data_store.run_names:
            raise RelaxNoPipeError, run

        # Initialise the sequence data if no sequence currently exists.
        if not relax_data_store.res.has_key(run):
            # Add the run to 'relax_data_store.res'.
            relax_data_store.res.add_list(run)

        # Test if the residue number already exists.
        for i in xrange(len(relax_data_store.res[run])):
            if relax_data_store.res[run][i].num == res_num:
                raise RelaxError, "The residue number '" + `res_num` + "' already exists in the sequence."

        # Residue index.
        index = len(relax_data_store.res[run])

        # Append a data container.
        relax_data_store.res[run].add_item()

        # Insert the data.
        relax_data_store.res[run][index].num = res_num
        relax_data_store.res[run][index].name = res_name
        relax_data_store.res[run][index].select = select


    def copy(self, run1=None, run2=None):
        """Function for copying the sequence from run1 to run2."""

        # Test if run1 exists.
        if not run1 in relax_data_store.run_names:
            raise RelaxNoPipeError, run1

        # Test if run2 exists.
        if not run2 in relax_data_store.run_names:
            raise RelaxNoPipeError, run2

        # Test if the sequence data for run1 is loaded.
        if not relax_data_store.res.has_key(run1):
            raise RelaxNoSequenceError, run1

        # Test if the sequence data already exists.
        if relax_data_store.res.has_key(run2):
            raise RelaxSequenceError, run2

        # Add run2 to 'relax_data_store.res'.
        relax_data_store.res.add_list(run2)

        # Copy the data.
        for i in xrange(len(relax_data_store.res[run1])):
            # Append a data container to run2.
            relax_data_store.res[run2].add_item()

            # Insert the data.
            relax_data_store.res[run2][i].num = relax_data_store.res[run1][i].num
            relax_data_store.res[run2][i].name = relax_data_store.res[run1][i].name
            relax_data_store.res[run2][i].select = relax_data_store.res[run1][i].select


    def data_names(self):
        """Function for returning a list of names of data structures associated with the sequence."""

        return [ 'res' ]


    def delete(self, run=None):
        """Function for deleting the sequence."""

        # Test if the run exists.
        if not run in relax_data_store.run_names:
            raise RelaxNoPipeError, run

        # Test if the sequence data is loaded.
        if not relax_data_store.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Delete the data.
        del(relax_data_store.res[run])

        # Clean up the runs.
        self.relax.generic.runs.eliminate_unused_runs()


    def display(self, run=None):
        """Function for displaying the sequence."""

        # Test if the run exists.
        if not run in relax_data_store.run_names:
            raise RelaxNoPipeError, run

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


    def sort(self, run=None):
        """Function for sorting the sequence by residue number."""

        # Test if the run exists.
        if not run in relax_data_store.run_names:
            raise RelaxNoPipeError, run

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
            raise RelaxNoPipeError, run

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
