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

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import count_spins, exists_mol_res_spin_data, generate_spin_id, return_molecule, return_residue, return_spin, spin_loop
from relax_errors import RelaxError, RelaxFileEmptyError, RelaxNoPdbChainError, RelaxNoPipeError, RelaxNoSequenceError, RelaxSequenceError
from relax_io import extract_data, open_write_file, strip
import sys



def display(sep=None, mol_name_flag=False, res_num_flag=False, res_name_flag=False, spin_num_flag=False, spin_name_flag=False):
    """Function for displaying the molecule, residue, and/or spin sequence data.

    This calls the write_body() function to do most of the work.


    @keyword sep:               The column seperator which, if None, defaults to whitespace.
    @type sep:                  str or None
    @keyword mol_name_flag:     A flag which if True will cause the molecule name column to be
                                written.
    @type mol_name_flag:        bool
    @keyword res_num_flag:      A flag which if True will cause the residue number column to be
                                written.
    @type res_num_flag:         bool
    @keyword res_name_flag:     A flag which if True will cause the residue name column to be
                                written.
    @type res_name_flag:        bool
    @keyword spin_name_flag:    A flag which if True will cause the spin name column to be written.
    @type spin_name_flag:       bool
    @keyword spin_num_flag:     A flag which if True will cause the spin number column to be
                                written.
    @type spin_num_flag:        bool
    @param mol_name_flag:    The column to contain the molecule name information.
    """

    # Test if the sequence data is loaded.
    if not count_spins():
        raise RelaxNoSequenceError

    # Write the data.
    write_body(file=sys.stdout, sep=sep, mol_name_flag=mol_name_flag, res_num_flag=res_num_flag, res_name_flag=res_name_flag, spin_num_flag=spin_num_flag, spin_name_flag=spin_name_flag)


def generate(mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None):
    """Generate the sequence item-by-item by adding a single molecule/residue/spin container as necessary.

    @keyword mol_name:          The molecule name.
    @type mol_name:             bool
    @keyword res_num:           The residue number.
    @type res_num:              bool
    @keyword res_name:          The residue name.
    @type res_name:             bool
    @keyword spin_num:          The spin number.
    @type spin_num:             bool
    @keyword spin_name:         The spin name.
    @type spin_name:            bool
    """

    # Alias the current data pipe.
    cdp = ds[ds.current_pipe]

    # Get the molecule.
    curr_mol = return_molecule(generate_spin_id(mol_name=mol_name))

    # A new molecule.
    if not curr_mol:
        # Add the molecule (and store it in the 'curr_mol' object).
        cdp.mol.add_item(mol_name=mol_name)
        curr_mol = cdp.mol[-1]

    # Get the residue.
    curr_res = return_residue(generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name))

    # A new residue.
    if not curr_res:
        # Add the residue (and store it in the 'curr_res' object).
        curr_mol.res.add_item(res_name=res_name, res_num=res_num)
        curr_res = curr_mol.res[-1]

    # Get the spin.
    curr_spin = return_spin(generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name))

    # A new spin.
    if not curr_spin:
        # Add the spin.
        curr_res.spin.add_item(spin_name=spin_name, spin_num=spin_num)

    # Print out of all the spins.
    write_line(sys.stdout, mol_name, res_num, res_name, spin_num, spin_name, mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True)


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
    if exists_mol_res_spin_data():
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

    # Test if the sequence data is valid.
    validate_sequence(file_data, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col)

    # Header print out.
    write_header(sys.stdout, mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True)

    # Fill the molecule-residue-spin data.
    for i in xrange(len(file_data)):
        # The spin info.
        mol_name = None
        res_num = None
        res_name = None
        spin_num = None
        spin_name = None
        if mol_name_col != None:
            mol_name = file_data[i][mol_name_col]
        if res_num_col != None:
            res_num = int(file_data[i][res_num_col])
        if res_name_col != None:
            res_name = file_data[i][res_name_col]
        if spin_num_col != None:
            spin_num = int(file_data[i][spin_num_col])
        if spin_name_col != None:
            spin_name = file_data[i][spin_name_col]

        # Generate the sequence.
        generate(mol_name, res_num, res_name, spin_num, spin_name)


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


def write(file, dir=None, sep=None, mol_name_flag=False, res_num_flag=False, res_name_flag=False, spin_num_flag=False, spin_name_flag=False, force=False):
    """Function for writing molecule, residue, and/or sequence data.

    This calls the write_body() function to do most of the work.


    @param file:                The name of the file to write the data to.
    @type file:                 str
    @keyword dir:               The directory to contain the file (defaults to the current directory
                                if None).
    @type dir:                  str or None
    @keyword sep:               The column seperator which, if None, defaults to whitespace.
    @type sep:                  str or None
    @keyword mol_name_flag:     A flag which if True will cause the molecule name column to be
                                written.
    @type mol_name_flag:        bool
    @keyword res_num_flag:      A flag which if True will cause the residue number column to be
                                written.
    @type res_num_flag:         bool
    @keyword res_name_flag:     A flag which if True will cause the residue name column to be
                                written.
    @type res_name_flag:        bool
    @keyword spin_name_flag:    A flag which if True will cause the spin name column to be written.
    @type spin_name_flag:       bool
    @keyword spin_num_flag:     A flag which if True will cause the spin number column to be
                                written.
    @keyword force:             A flag which if True will cause an existing file to be overwritten.
    @type force:                bin
    """

    # Test if the sequence data is loaded.
    if not count_spins():
        raise RelaxNoSequenceError

    # Open the file for writing.
    seq_file = open_write_file(file, dir, force)

    # Write the data.
    write_body(file=seq_file, sep=sep, mol_name_flag=mol_name_flag, res_num_flag=res_num_flag, res_name_flag=res_name_flag, spin_num_flag=spin_num_flag, spin_name_flag=spin_name_flag)

    # Close the results file.
    seq_file.close()



def write_body(file=None, sep=None, mol_name_flag=False, res_num_flag=False, res_name_flag=False, spin_num_flag=False, spin_name_flag=False):
    """Function for writing to the given file object the molecule, residue, and/or sequence data.

    @param file:                The file to write the data to.
    @type file:                 writable file object
    @keyword sep:               The column seperator which, if None, defaults to whitespace.
    @type sep:                  str or None
    @keyword mol_name_flag:     A flag which if True will cause the molecule name column to be
                                written.
    @type mol_name_flag:        bool
    @keyword res_num_flag:      A flag which if True will cause the residue number column to be
                                written.
    @type res_num_flag:         bool
    @keyword res_name_flag:     A flag which if True will cause the residue name column to be
                                written.
    @type res_name_flag:        bool
    @keyword spin_name_flag:    A flag which if True will cause the spin name column to be written.
    @type spin_name_flag:       bool
    @keyword spin_num_flag:     A flag which if True will cause the spin number column to be
                                written.
    @type spin_num_flag:        bool
    """

    # No special seperator character.
    if sep == None:
        sep = ''

    # Write the header.
    write_header(file, sep=sep, mol_name_flag=mol_name_flag, res_num_flag=res_num_flag, res_name_flag=res_name_flag, spin_num_flag=spin_num_flag, spin_name_flag=spin_name_flag)

    # Loop over the spins.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        write_line(file, mol_name, res_num, res_name, spin.num, spin.name, sep=sep, mol_name_flag=mol_name_flag, res_num_flag=res_num_flag, res_name_flag=res_name_flag, spin_num_flag=spin_num_flag, spin_name_flag=spin_name_flag)


def write_header(file, sep=None, mol_name_flag=False, res_num_flag=False, res_name_flag=False, spin_num_flag=False, spin_name_flag=False):
    """Function for writing to the given file object the molecule, residue, and/or sequence data.

    @param file:                The file to write the data to.
    @type file:                 writable file object
    @keyword sep:               The column seperator which, if None, defaults to whitespace.
    @type sep:                  str or None
    @keyword mol_name_flag:     A flag which if True will cause the molecule name column to be
                                written.
    @type mol_name_flag:        bool
    @keyword res_num_flag:      A flag which if True will cause the residue number column to be
                                written.
    @type res_num_flag:         bool
    @keyword res_name_flag:     A flag which if True will cause the residue name column to be
                                written.
    @type res_name_flag:        bool
    @keyword spin_name_flag:    A flag which if True will cause the spin name column to be written.
    @type spin_name_flag:       bool
    @keyword spin_num_flag:     A flag which if True will cause the spin number column to be
                                written.
    @type spin_num_flag:        bool
    """

    # No special seperator character.
    if sep == None:
        sep = ''

    # Write the header.
    if mol_name_flag:
        file.write("%-10s " % ("Mol_name"+sep))
    if res_num_flag:
        file.write("%-10s " % ("Res_num"+sep))
    if res_name_flag:
        file.write("%-10s " % ("Res_name"+sep))
    if spin_num_flag:
        file.write("%-10s " % ("Spin_num"+sep))
    if spin_name_flag:
        file.write("%-10s " % ("Spin_name"+sep))
    file.write('\n')


def write_line(file, mol_name, res_num, res_name, spin_num, spin_name, sep=None, mol_name_flag=False, res_num_flag=False, res_name_flag=False, spin_num_flag=False, spin_name_flag=False):
    """Write to the given file object a single line of molecule, residue, and spin data.

    @param file:                The file to write the data to.
    @type file:                 writable file object
    @param mol_name:            The molecule name.
    @type mol_name:             anything
    @param res_num:             The residue number.
    @type res_num:              anything
    @param res_name:            The residue name.
    @type res_name:             anything
    @param spin_num:            The spin number.
    @type spin_num:             anything
    @param spin_name:           The spin name.
    @type spin_name:            anything
    @keyword sep:               The column seperator which, if None, defaults to whitespace.
    @type sep:                  str or None
    @keyword mol_name_flag:     A flag which if True will cause the molecule name column to be
                                written.
    @type mol_name_flag:        bool
    @keyword res_num_flag:      A flag which if True will cause the residue number column to be
                                written.
    @type res_num_flag:         bool
    @keyword res_name_flag:     A flag which if True will cause the residue name column to be
                                written.
    @type res_name_flag:        bool
    @keyword spin_name_flag:    A flag which if True will cause the spin name column to be written.
    @type spin_name_flag:       bool
    @keyword spin_num_flag:     A flag which if True will cause the spin number column to be
                                written.
    @type spin_num_flag:        bool
    """

    # No special seperator character.
    if sep == None:
        sep = ''

    # Write the header.
    if mol_name_flag:
        file.write("%-10s " % (str(mol_name)+sep))
    if res_num_flag:
        file.write("%-10s " % (str(res_num)+sep))
    if res_name_flag:
        file.write("%-10s " % (str(res_name)+sep))
    if spin_num_flag:
        file.write("%-10s " % (str(spin_num)+sep))
    if spin_name_flag:
        file.write("%-10s " % (str(spin_name)+sep))
    file.write('\n')
