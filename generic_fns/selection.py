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
"""Module for selecting and deselecting spins."""

# Python module imports
from warnings import warn

# relax module imports.
from generic_fns.mol_res_spin import exists_mol_res_spin_data, generate_spin_id_data_array, return_spin, spin_loop
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoSequenceError
from relax_io import read_spin_data
from relax_warnings import RelaxNoSpinWarning


def desel_all():
    """Deselect all spins.

    @raises RelaxNoSequenceError:   If no molecule/residue/spins sequence data exists.
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Loop over the spins and deselect them.
    for spin in spin_loop():
        spin.select = False


def desel_read(file=None, dir=None, file_data=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, spin_id=None, boolean='AND', change_all=False):
    """Deselect the spins contained in the given file.

    @keyword file:                  The name of the file to open.
    @type file:                     str
    @keyword dir:                   The directory containing the file (defaults to the current
                                    directory if None).
    @type dir:                      str or None
    @keyword file_data:             An alternative opening a file, if the data already exists in the
                                    correct format.  The format is a list of lists where the first
                                    index corresponds to the row and the second the column.
    @type file_data:                list of lists
    @keyword spin_id_col:           The column containing the spin ID strings.  If supplied, the
                                    mol_name_col, res_name_col, res_num_col, spin_name_col, and
                                    spin_num_col arguments must be none.
    @type spin_id_col:              int or None
    @keyword mol_name_col:          The column containing the molecule name information.  If
                                    supplied, spin_id_col must be None.
    @type mol_name_col:             int or None
    @keyword res_name_col:          The column containing the residue name information.  If
                                    supplied, spin_id_col must be None.
    @type res_name_col:             int or None
    @keyword res_num_col:           The column containing the residue number information.  If
                                    supplied, spin_id_col must be None.
    @type res_num_col:              int or None
    @keyword spin_name_col:         The column containing the spin name information.  If supplied,
                                    spin_id_col must be None.
    @type spin_name_col:            int or None
    @keyword spin_num_col:          The column containing the spin number information.  If supplied,
                                    spin_id_col must be None.
    @type spin_num_col:             int or None
    @keyword sep:                   The column separator which, if None, defaults to whitespace.
    @type sep:                      str or None
    @keyword spin_id:               The spin ID string used to restrict data loading to a subset of
                                    all spins.
    @type spin_id:                  None or str
    @param boolean:                 The boolean operator used to deselect the spin systems with.  It
                                    can be one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'.
                                    This will be ignored if the change_all flag is set.
    @type boolean:                  str
    @keyword change_all:            A flag which if True will cause all spins not specified in the
                                    file to be selected.  Only the boolean operator 'AND' is
                                    compatible with this flag set to True (all others will be
                                    ignored).
    @type change_all:               bool
    @raises RelaxNoSequenceError:   If no molecule/residue/spins sequence data exists.
    @raises RelaxError:             If the boolean operator is unknown.
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # First select all spins if the change_all flag is set.
    if change_all:
        for spin in spin_loop():
            spin.select = True

    # Then deselect the spins in the file.
    for id in read_spin_data(file=file, dir=dir, file_data=file_data, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id):
        # Get the corresponding spin container.
        spin = return_spin(id)

        # No spin.
        if spin == None:
            warn(RelaxNoSpinWarning(id))
            continue

        # Deselect the spin.
        if change_all:
            spin.select = False

        # Boolean selections.
        else:
            if boolean == 'OR':
                spin.select = spin.select or False
            elif boolean == 'NOR':
                spin.select = not (spin.select or False)
            elif boolean == 'AND':
                spin.select = spin.select and False
            elif boolean == 'NAND':
                spin.select = not (spin.select and False)
            elif boolean == 'XOR':
                spin.select = not (spin.select and False) and (spin.select or False)
            elif boolean == 'XNOR':
                spin.select = (spin.select and False) or not (spin.select or False)
            else:
                raise RelaxError("Unknown boolean operator " + repr(boolean))


def desel_spin(spin_id=None, boolean='AND', change_all=False):
    """Deselect specific spins.

    @keyword spin_id:               The spin identification string.
    @type spin_id:                  str or None
    @param boolean:                 The boolean operator used to deselect the spin systems with.  It
                                    can be one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'.
                                    This will be ignored if the change_all flag is set.
    @type boolean:                  str
    @keyword change_all:            A flag which if True will cause all spins not specified in the
                                    file to be selected.  Only the boolean operator 'AND' is
                                    compatible with this flag set to True (all others will be
                                    ignored).
    @type change_all:               bool
    @raises RelaxNoSequenceError:   If no molecule/residue/spins sequence data exists.
    @raises RelaxError:             If the boolean operator is unknown.
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # First select all spins if the change_all flag is set.
    if change_all:
        for spin in spin_loop():
            spin.select = True

    # Loop over the specified spins.
    for spin in spin_loop(spin_id):
        # Deselect just the specified residues.
        if change_all:
            spin.select = False

        # Boolean selections.
        else:
            if boolean == 'OR':
                spin.select = spin.select or False
            elif boolean == 'NOR':
                spin.select = not (spin.select or False)
            elif boolean == 'AND':
                spin.select = spin.select and False
            elif boolean == 'NAND':
                spin.select = not (spin.select and False)
            elif boolean == 'XOR':
                spin.select = not (spin.select and False) and (spin.select or False)
            elif boolean == 'XNOR':
                spin.select = (spin.select and False) or not (spin.select or False)
            else:
                raise RelaxError("Unknown boolean operator " + repr(boolean))


def is_mol_selected(selection=None):
    """Query if the molecule is selected.

    @keyword selection:     The molecule ID string.
    @type selection:        str
    """

    # Find if any spins are selected.
    select = False
    for spin in spin_loop(selection):
        if spin.select:
            select = True
            break

    # Return the state.
    return select


def is_res_selected(selection=None):
    """Query if the residue is selected.

    @keyword selection:     The residue ID string.
    @type selection:        str
    """

    # Find if any spins are selected.
    select = False
    for spin in spin_loop(selection):
        if spin.select:
            select = True
            break

    # Return the state.
    return select


def is_spin_selected(selection=None):
    """Query if the spin is selected.

    @keyword selection:     The molecule ID string.
    @type selection:        str
    """

    # Get the spin.
    spin = return_spin(selection)

    # Return the selected state.
    return spin.select


def reverse(spin_id=None):
    """Reversal of spin selections.

    @keyword spin_id:               The spin identification string.
    @type spin_id:                  str or None
    @raises RelaxNoSequenceError:   If no molecule/residue/spins sequence data exists.
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Loop over the spin systems and reverse the selection flag.
    for spin in spin_loop(spin_id):
        # Reverse the selection.
        if spin.select:
            spin.select = False
        else:
            spin.select = True


def sel_all():
    """Select all residues.

    @raises RelaxNoSequenceError:   If no molecule/residue/spins sequence data exists.
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Loop over the spins and select them.
    for spin in spin_loop():
        spin.select = True


def sel_read(file=None, dir=None, file_data=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, spin_id=None, boolean='OR', change_all=False):
    """Select the spins contained in the given file.

    @keyword file:                  The name of the file to open.
    @type file:                     str
    @keyword dir:                   The directory containing the file (defaults to the current
                                    directory if None).
    @type dir:                      str or None
    @keyword file_data:             An alternative opening a file, if the data already exists in the
                                    correct format.  The format is a list of lists where the first
                                    index corresponds to the row and the second the column.
    @type file_data:                list of lists
    @keyword spin_id_col:           The column containing the spin ID strings.  If supplied, the
                                    mol_name_col, res_name_col, res_num_col, spin_name_col, and
                                    spin_num_col arguments must be none.
    @type spin_id_col:              int or None
    @keyword mol_name_col:          The column containing the molecule name information.  If
                                    supplied, spin_id_col must be None.
    @type mol_name_col:             int or None
    @keyword res_name_col:          The column containing the residue name information.  If
                                    supplied, spin_id_col must be None.
    @type res_name_col:             int or None
    @keyword res_num_col:           The column containing the residue number information.  If
                                    supplied, spin_id_col must be None.
    @type res_num_col:              int or None
    @keyword spin_name_col:         The column containing the spin name information.  If supplied,
                                    spin_id_col must be None.
    @type spin_name_col:            int or None
    @keyword spin_num_col:          The column containing the spin number information.  If supplied,
                                    spin_id_col must be None.
    @type spin_num_col:             int or None
    @keyword sep:                   The column separator which, if None, defaults to whitespace.
    @type sep:                      str or None
    @keyword spin_id:               The spin ID string used to restrict data loading to a subset of
                                    all spins.
    @type spin_id:                  None or str
    @param boolean:                 The boolean operator used to select the spin systems with.  It
                                    can be one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'.
                                    This will be ignored if the change_all flag is set.
    @type boolean:                  str
    @keyword change_all:            A flag which if True will cause all spins not specified in the
                                    file to be deselected.  Only the boolean operator 'OR' is
                                    compatible with this flag set to True (all others will be
                                    ignored).
    @type change_all:               bool
    @raises RelaxNoSequenceError:   If no molecule/residue/spins sequence data exists.
    @raises RelaxError:             If the boolean operator is unknown.
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # First deselect all spins if the change_all flag is set.
    if change_all:
        # Loop over all spins.
        for spin in spin_loop():
            spin.select = False

    # Then deselect the spins in the file.
    for id in read_spin_data(file=file, dir=dir, file_data=file_data, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id):
        # Get the corresponding spin container.
        spin = return_spin(id)

        # No spin.
        if spin == None:
            warn(RelaxNoSpinWarning(id))
            continue

        # Select the spin.
        if change_all:
            spin.select = True

        # Boolean selections.
        else:
            if boolean == 'OR':
                spin.select = spin.select or True
            elif boolean == 'NOR':
                spin.select = not (spin.select or True)
            elif boolean == 'AND':
                spin.select = spin.select and True
            elif boolean == 'NAND':
                spin.select = not (spin.select and True)
            elif boolean == 'XOR':
                spin.select = not (spin.select and True) and (spin.select or True)
            elif boolean == 'XNOR':
                spin.select = (spin.select and True) or not (spin.select or True)
            else:
                raise RelaxError("Unknown boolean operator " + repr(boolean))


def sel_spin(spin_id=None, boolean='OR', change_all=False):
    """Select specific spins.

    @keyword spin_id:               The spin identification string.
    @type spin_id:                  str or None
    @param boolean:                 The boolean operator used to select the spin systems with.  It
                                    can be one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'.
                                    This will be ignored if the change_all flag is set.
    @type boolean:                  str
    @keyword change_all:            A flag which if True will cause all spins not specified in the
                                    file to be deselected.  Only the boolean operator 'OR' is
                                    compatible with this flag set to True (all others will be
                                    ignored).
    @type change_all:               bool
    @raises RelaxNoSequenceError:   If no molecule/residue/spins sequence data exists.
    @raises RelaxError:             If the boolean operator is unknown.
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # First deselect all spins if the change_all flag is set.
    if change_all:
        # Loop over all spins.
        for spin in spin_loop():
            spin.select = False

    # Loop over the specified spins.
    for spin in spin_loop(spin_id):
        # Select just the specified residues.
        if change_all:
            spin.select = True

        # Boolean selections.
        else:
            if boolean == 'OR':
                spin.select = spin.select or True
            elif boolean == 'NOR':
                spin.select = not (spin.select or True)
            elif boolean == 'AND':
                spin.select = spin.select and True
            elif boolean == 'NAND':
                spin.select = not (spin.select and True)
            elif boolean == 'XOR':
                spin.select = not (spin.select and True) and (spin.select or True)
            elif boolean == 'XNOR':
                spin.select = (spin.select and True) or not (spin.select or True)
            else:
                raise RelaxError("Unknown boolean operator " + repr(boolean))
