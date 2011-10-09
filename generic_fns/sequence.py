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
"""Module for handling the molecule, residue, and spin sequence."""

# Python module imports
from types import IntType, NoneType

# relax module imports.
from generic_fns.mol_res_spin import count_molecules, count_residues, count_spins, exists_mol_res_spin_data, generate_spin_id, return_molecule, return_residue, return_spin, spin_id_to_data_list, spin_loop
import pipes
from relax_errors import RelaxError, RelaxDiffMolNumError, RelaxDiffResNumError, RelaxDiffSeqError, RelaxDiffSpinNumError, RelaxFileEmptyError, RelaxInvalidSeqError, RelaxNoSequenceError, RelaxSequenceError
from relax_io import open_write_file, read_spin_data, write_spin_data
import sys



def copy(pipe_from=None, pipe_to=None, preserve_select=False, verbose=True):
    """Copy the molecule, residue, and spin sequence data from one data pipe to another.

    @keyword pipe_from:         The data pipe to copy the sequence data from.  This defaults to the
                                current data pipe.
    @type pipe_from:            str
    @keyword pipe_to:           The data pipe to copy the sequence data to.  This defaults to the
                                current data pipe.
    @type pipe_to:              str
    @keyword preserve_select:   A flag which if True will cause spin selections to be preserved.
    @type preserve_select:      bool
    @keyword verbose:           A flag which if True will cause info about each spin to be printed
                                out as the sequence is generated.
    @type verbose:              bool
    """

    # Defaults.
    if pipe_from == None and pipe_to == None:
        raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")
    elif pipe_from == None:
        pipe_from = pipes.cdp_name()
    elif pipe_to == None:
        pipe_to = pipes.cdp_name()

    # Test if the pipe_from and pipe_to data pipes exist.
    pipes.test(pipe_from)
    pipes.test(pipe_to)

    # Test if pipe_from contains sequence data.
    if not exists_mol_res_spin_data(pipe_from):
        raise RelaxNoSequenceError

    # Test if pipe_to contains sequence data.
    if exists_mol_res_spin_data(pipe_to):
        raise RelaxSequenceError

    # Loop over the spins of the pipe_from data pipe.
    for spin, mol_name, res_num, res_name in spin_loop(pipe=pipe_from, full_info=True):
        # Preserve selection.
        if preserve_select:
            select = spin.select
        else:
            select = True

        # Generate the new sequence.
        generate(mol_name, res_num, res_name, spin.num, spin.name, pipe_to, select=select, verbose=verbose)


def compare_sequence(pipe1=None, pipe2=None, fail=True):
    """Compare the sequence in two data pipes.

    @keyword pipe1:     The name of the first data pipe.
    @type pipe1:        str
    @keyword pipe2:     The name of the second data pipe.
    @type pipe2:        str
    @keyword fail:      A flag which if True causes a RelaxError to be raised.
    @type fail:         bool
    @return:            1 if the sequence is the same, 0 if different.
    @rtype:             int
    @raises RelaxError: If the sequence is different and the fail flag is True.
    """

    # Failure status.
    status = 1

    # Molecule number.
    if count_molecules(pipe=pipe1) != count_molecules(pipe=pipe2):
        status = 0
        if fail:
            raise RelaxDiffMolNumError(pipe1, pipe2)

    # Residue number.
    if count_residues(pipe=pipe1) != count_residues(pipe=pipe2):
        status = 0
        if fail:
            raise RelaxDiffResNumError(pipe1, pipe2)

    # Spin number.
    if count_spins(pipe=pipe1) != count_spins(pipe=pipe2):
        status = 0
        if fail:
            raise RelaxDiffSpinNumError(pipe1, pipe2)

    # Create a string representation of the 2 sequences.
    seq1 = ''
    seq2 = ''
    for spin, spin_id in spin_loop(return_id=True, pipe=pipe1):
        seq1 = seq1 + spin_id + '\n'
    for spin, spin_id in spin_loop(return_id=True, pipe=pipe2):
        seq2 = seq2 + spin_id + '\n'

    # Sequence check.
    if seq1 != seq2:
        status = 0
        if fail:
            raise RelaxDiffSeqError(pipe1, pipe2)

    # Return the status.
    return status


def display(sep=None, mol_name_flag=False, res_num_flag=False, res_name_flag=False, spin_num_flag=False, spin_name_flag=False):
    """Display the molecule, residue, and/or spin sequence data.

    This calls the write() function to do most of the work.


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
    write(file=sys.stdout, sep=sep, mol_name_flag=mol_name_flag, res_num_flag=res_num_flag, res_name_flag=res_name_flag, spin_num_flag=spin_num_flag, spin_name_flag=spin_name_flag)


def generate(mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None, pipe=None, select=True, verbose=True):
    """Generate the sequence item-by-item by adding a single molecule/residue/spin container as necessary.

    @keyword mol_name:  The molecule name.
    @type mol_name:     str or None
    @keyword res_num:   The residue number.
    @type res_num:      int or None
    @keyword res_name:  The residue name.
    @type res_name:     str or None
    @keyword spin_num:  The spin number.
    @type spin_num:     int or None
    @keyword spin_name: The spin name.
    @type spin_name:    str or None
    @keyword pipe:      The data pipe in which to generate the sequence.  This defaults to the
                        current data pipe.
    @type pipe:         str
    @keyword select:    The spin selection flag.
    @type select:       bool
    @keyword verbose:   A flag which if True will cause info about each spin to be printed out as
                        the sequence is generated.
    @type verbose:      bool
    """

    # The current data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Get the molecule.
    curr_mol = return_molecule(generate_spin_id(mol_name=mol_name), pipe=pipe)

    # A new molecule.
    if not curr_mol:
        # Add the molecule (and store it in the 'curr_mol' object).
        dp.mol.add_item(mol_name=mol_name)
        curr_mol = dp.mol[-1]

    # Get the residue.
    curr_res = return_residue(generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name), pipe=pipe)

    # A new residue.
    if not curr_res:
        # Add the residue (and store it in the 'curr_res' object).
        curr_mol.res.add_item(res_name=res_name, res_num=res_num)
        curr_res = curr_mol.res[-1]

    # Get the spin.
    curr_spin = return_spin(generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name), pipe=pipe)

    # A new spin.
    new_data = False
    if not curr_spin:
        # Add the spin.
        curr_res.spin.add_item(spin_name=spin_name, spin_num=spin_num)

        # Get the spin.
        curr_spin = return_spin(generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name), pipe=pipe)

        # New data.
        new_data = True

    # Set the selection flag.
    curr_spin.select = select

    # Print out of all the spins.
    if new_data:
        return mol_name, res_num, res_name, spin_num, spin_name


def read(file=None, dir=None, file_data=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, spin_id=None):
    """Read the molecule, residue, and/or spin sequence data from file.

    @param file:            The name of the file to open.
    @type file:             str
    @param dir:             The directory containing the file (defaults to the current directory if
                            None).
    @type dir:              str or None
    @keyword file_data:     An alternative to opening a file, if the data already exists in the
                            correct format.  The format is a list of lists where the first index
                            corresponds to the row and the second the column.
    @type file_data:        list of lists
    @keyword spin_id_col:   The column containing the spin ID strings.  If supplied, the
                            mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col
                            arguments must be none.
    @type spin_id_col:      int or None
    @keyword mol_name_col:  The column containing the molecule name information.  If supplied,
                            spin_id_col must be None.
    @type mol_name_col:     int or None
    @keyword res_name_col:  The column containing the residue name information.  If supplied,
                            spin_id_col must be None.
    @type res_name_col:     int or None
    @keyword res_num_col:   The column containing the residue number information.  If supplied,
                            spin_id_col must be None.
    @type res_num_col:      int or None
    @keyword spin_name_col: The column containing the spin name information.  If supplied,
                            spin_id_col must be None.
    @type spin_name_col:    int or None
    @keyword spin_num_col:  The column containing the spin number information.  If supplied,
                            spin_id_col must be None.
    @type spin_num_col:     int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword spin_id:       The spin ID string used to restrict data loading to a subset of all
                            spins.
    @type spin_id:          None or str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data already exists.
    if exists_mol_res_spin_data():
        raise RelaxSequenceError

    # Init the data.
    mol_names = []
    res_nums = []
    res_names = []
    spin_nums = []
    spin_names = []

    # Generate the sequence.
    for id in read_spin_data(file=file, dir=dir, file_data=file_data, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id):
        # Add the spin.
        new_spin = generate(*spin_id_to_data_list(id))

        # Append the new spin.
        if new_spin:
            mol_names.append(new_spin[0])
            res_nums.append(new_spin[1])
            res_names.append(new_spin[2])
            spin_nums.append(new_spin[3])
            spin_names.append(new_spin[4])

    # Write the data.
    write_spin_data(sys.stdout, mol_names=mol_names, res_nums=res_nums, res_names=res_names, spin_nums=spin_nums, spin_names=spin_names)


def validate_sequence(data, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None):
    """Test if the sequence data is valid.

    The only function this performs is to raise a RelaxError if the data is invalid.


    @param data:            The sequence data.
    @type data:             list of lists.
    @keyword spin_id_col:   The column containing the spin ID strings.
    @type spin_id_col:      int or None
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

    # Spin ID.
    if spin_id_col:
        if len(data) < spin_id_col:
            raise RelaxInvalidSeqError(data, "the Spin ID data is missing")

    # Molecule name data.
    if mol_name_col:
        if len(data) < mol_name_col:
            raise RelaxInvalidSeqError(data, "the molecule name data is missing")

    # Residue number data.
    if res_num_col:
        # No data in column.
        if len(data) < res_num_col:
            raise RelaxInvalidSeqError(data, "the residue number data is missing")

        # Bad data in column.
        try:
            res_num = eval(data[res_num_col-1])
            if not (isinstance(res_num, NoneType) or isinstance(res_num, IntType)):
                raise ValueError
        except:
            raise RelaxInvalidSeqError(data, "the residue number data '%s' is invalid" % data[res_num_col-1])

    # Residue name data.
    if res_name_col:
        if len(data) < res_name_col:
            raise RelaxInvalidSeqError(data, "the residue name data is missing")

    # Spin number data.
    if spin_num_col:
        # No data in column.
        if len(data) < spin_num_col:
            raise RelaxInvalidSeqError(data, "the spin number data is missing")

        # Bad data in column.
        try:
            res_num = eval(data[res_num_col-1])
            if not (isinstance(res_num, NoneType) or isinstance(res_num, IntType)):
                raise ValueError
        except:
            raise RelaxInvalidSeqError(data, "the spin number data '%s' is invalid" % data[res_num_col-1])

    # Spin name data.
    if spin_name_col:
        if len(data) < spin_name_col:
            raise RelaxInvalidSeqError(data, "the spin name data is missing")

    # Data.
    if data_col:
        if len(data) < data_col:
            raise RelaxInvalidSeqError(data, "the data is missing")

    # Errors
    if error_col:
        if len(data) < error_col:
            raise RelaxInvalidSeqError(data, "the error data is missing")


def write(file, dir=None, sep=None, mol_name_flag=False, res_num_flag=False, res_name_flag=False, spin_num_flag=False, spin_name_flag=False, force=False):
    """Write the molecule, residue, and/or sequence data.

    This calls the relax_io.write_spin_data() function to do most of the work.


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

    # Init the data.
    mol_names = []
    res_nums = []
    res_names = []
    spin_nums = []
    spin_names = []

    # Spin loop.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        mol_names.append(mol_name)
        res_nums.append(res_num)
        res_names.append(res_name)
        spin_nums.append(spin.num)
        spin_names.append(spin.name)

    # Remove unwanted data.
    if not mol_name_flag:
        mol_names = None
    if not res_num_flag:
        res_nums = None
    if not res_name_flag:
        res_names = None
    if not spin_num_flag:
        spin_nums = None
    if not spin_name_flag:
        spin_names = None

    # Write the data.
    write_spin_data(file=file, dir=dir, sep=sep, mol_names=mol_names, res_nums=res_nums, res_names=res_names, spin_nums=spin_nums, spin_names=spin_names, force=force)
