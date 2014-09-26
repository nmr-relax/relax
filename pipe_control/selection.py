###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for selecting and deselecting spins."""

# Python module imports
import sys
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoDomainError, RelaxNoSequenceError
from lib.selection import Selection, spin_id_to_data_list
from lib.sequence import read_spin_data, write_spin_data
from lib.warnings import RelaxNoSpinWarning
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import check_mol_res_spin_data, exists_mol_res_spin_data, generate_spin_id_unique, return_spin, spin_loop
from pipe_control.pipes import check_pipe
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container


boolean_doc = Desc_container("Boolean operators")
boolean_doc.add_paragraph("The boolean operator can be used to change how spin systems or interatomic data containers are selected.  The allowed values are: 'OR', 'NOR', 'AND', 'NAND', 'XOR', 'XNOR'.  The following table details how the selections will occur for the different boolean operators.")
table = uf_tables.add_table(label="table: bool operators", caption="Boolean operators and their effects on selections")
table.add_headings(["Spin system or interatomic data container", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
table.add_row(["Original selection", "0", "1", "1", "1", "1", "0", "1", "0", "1"])
table.add_row(["New selection", "0", "1", "1", "1", "1", "1", "0", "0", "0"])
table.add_row(["OR", "0", "1", "1", "1", "1", "1", "1", "0", "1"])
table.add_row(["NOR", "1", "0", "0", "0", "0", "0", "0", "1", "0"])
table.add_row(["AND", "0", "1", "1", "1", "1", "0", "0", "0", "0"])
table.add_row(["NAND", "1", "0", "0", "0", "0", "1", "1", "1", "1"])
table.add_row(["XOR", "0", "0", "0", "0", "0", "1", "1", "0", "1"])
table.add_row(["XNOR", "1", "1", "1", "1", "1", "0", "0", "1", "0"])
boolean_doc.add_table(table.label)


def boolean_deselect(current=None, boolean=None):
    """Return the new boolean deselection result using the current selection.

    @keyword current:   The current selection state.
    @type current:      bool
    @keyword boolean:   The boolean operator used to select with.  It can be one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'.
    @type boolean:      str
    @return:            The new selection state.
    @rtype:             bool
    """

    # Boolean selections.
    if boolean == 'OR':
        state = current or False
    elif boolean == 'NOR':
        state = not (current or False)
    elif boolean == 'AND':
        state = current and False
    elif boolean == 'NAND':
        state = not (current and False)
    elif boolean == 'XOR':
        state = not (current and False) and (current or False)
    elif boolean == 'XNOR':
        state = (current and False) or not (current or False)
    else:
        raise RelaxError("Unknown boolean operator " + repr(boolean))

    # Return the new selection state.
    return state


def boolean_select(current=None, boolean=None):
    """Return the new boolean selection result using the current selection.

    @keyword current:   The current selection state.
    @type current:      bool
    @keyword boolean:   The boolean operator used to select with.  It can be one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'.
    @type boolean:      str
    @return:            The new selection state.
    @rtype:             bool
    """

    # Boolean selections.
    if boolean == 'OR':
        state = current or True
    elif boolean == 'NOR':
        state = not (current or True)
    elif boolean == 'AND':
        state = current and True
    elif boolean == 'NAND':
        state = not (current and True)
    elif boolean == 'XOR':
        state = not (current and True) and (current or True)
    elif boolean == 'XNOR':
        state = (current and True) or not (current or True)
    else:
        raise RelaxError("Unknown boolean operator " + repr(boolean))

    # Return the new selection state.
    return state


def desel_all():
    """Deselect all spins.

    @raises RelaxNoSequenceError:   If no molecule/residue/spins sequence data exists.
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Loop over the spins and deselect them.
    for spin in spin_loop():
        spin.select = False


def desel_interatom(spin_id1=None, spin_id2=None, boolean='AND', change_all=False):
    """Deselect specific interatomic data containers.

    @keyword spin_id1:              The spin ID string of the first spin of the pair.
    @type spin_id1:                 str or None
    @keyword spin_id2:              The spin ID string of the second spin of the pair.
    @type spin_id2:                 str or None
    @param boolean:                 The boolean operator used to deselect the spin systems with.  It can be one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'. This will be ignored if the change_all flag is set.
    @type boolean:                  str
    @keyword change_all:            A flag which if True will cause all spins not specified in the file to be selected.  Only the boolean operator 'AND' is compatible with this flag set to True (all others will be ignored).
    @type change_all:               bool
    @raises RelaxNoSequenceError:   If no molecule/residue/spins sequence data exists.
    @raises RelaxError:             If the boolean operator is unknown.
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # First select all interatom containers if the change_all flag is set.
    if change_all:
        # Interatomic data loop.
        for interatom in interatomic_loop(skip_desel=False):
            interatom.select = True

    # Interatomic data loop.
    for interatom in interatomic_loop(selection1=spin_id1, selection2=spin_id2, skip_desel=False):
        # Deselect just the specified residues.
        if change_all:
            interatom.select = False

        # Boolean selections.
        else:
            interatom.select = boolean_deselect(current=interatom.select, boolean=boolean)


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
    check_pipe()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # First select all spins if the change_all flag is set.
    if change_all:
        for spin in spin_loop():
            spin.select = True

    # Then deselect the spins in the file.
    ids = []
    for mol_name, res_num, res_name, spin_num, spin_name in read_spin_data(file=file, dir=dir, file_data=file_data, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id):
        # Get the corresponding spin container.
        id = generate_spin_id_unique(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name)
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
            spin.select = boolean_deselect(current=spin.select, boolean=boolean)

        # Store the spin ID for printouts.
        if not spin.select:
            ids.append(id)

    # Printout.
    if not len(ids):
        print("No spins deselected.")
    else:
        print("The following spins were deselected:")
        for id in ids:
            print(id)


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
    check_pipe()

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
            spin.select = boolean_deselect(current=spin.select, boolean=boolean)


def display(sep=None, mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True):
    """Display the current spin selections.

    @keyword sep:               The column seperator which, if None, defaults to whitespace.
    @type sep:                  str or None
    @keyword mol_name_flag:     A flag which if True will cause the molecule name column to be written.
    @type mol_name_flag:        bool
    @keyword res_num_flag:      A flag which if True will cause the residue number column to be written.
    @type res_num_flag:         bool
    @keyword res_name_flag:     A flag which if True will cause the residue name column to be written.
    @type res_name_flag:        bool
    @keyword spin_name_flag:    A flag which if True will cause the spin name column to be written.
    @type spin_name_flag:       bool
    @keyword spin_num_flag:     A flag which if True will cause the spin number column to be written.
    @type spin_num_flag:        bool
    """

    # Test if the sequence data is loaded.
    check_mol_res_spin_data()

    # Init the data.
    mol_names = []
    res_nums = []
    res_names = []
    spin_nums = []
    spin_names = []
    selections = []

    # Spin loop.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True, skip_desel=False):
        mol_names.append(mol_name)
        res_nums.append(res_num)
        res_names.append(res_name)
        spin_nums.append(spin.num)
        spin_names.append(spin.name)
        selections.append(spin.select)

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
    write_spin_data(file=sys.stdout, sep=sep, mol_names=mol_names, res_nums=res_nums, res_names=res_names, spin_nums=spin_nums, spin_names=spin_names, data=selections, data_name="selection")


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
    check_pipe()

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
    check_pipe()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Loop over the spins and select them.
    for spin in spin_loop():
        spin.select = True


def sel_domain(domain_id=None, boolean='OR', change_all=False):
    """Select all spins and interatomic data containers of the given domain.

    @keyword domain_id:     The domain ID string.
    @type domain_id:        str or None
    @param boolean:         The boolean operator used to select the spin systems with.  It can be one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'. This will be ignored if the change_all flag is set.
    @type boolean:          str
    @keyword change_all:    A flag which if True will cause all spins and interatomic data containers outside of the domain to be deselected.
    @type change_all:       bool
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Test if the domain is defined.
    if not hasattr(cdp, 'domain') or domain_id not in cdp.domain:
        raise RelaxNoDomainError(domain_id)

    # The domain selection object.
    domain = Selection(cdp.domain[domain_id])

    # Loop over the spins and select as required.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # Inside the domain.
        if domain.contains_spin(spin_name=spin.name, spin_num=spin.num, res_name=res_name, res_num=res_num, mol=mol_name):
            spin.select = boolean_select(current=spin.select, boolean=boolean)

        # Deselect spins outside of the domain.
        elif change_all:
            spin.select = False

    # Interatomic data loop.
    for interatom in interatomic_loop():
        # Decode the spin ids.
        mol_name1, res_num1, res_name1, spin_num1, spin_name1 = spin_id_to_data_list(interatom.spin_id1)
        mol_name2, res_num2, res_name2, spin_num2, spin_name2 = spin_id_to_data_list(interatom.spin_id2)

        # Inside the domain.
        if domain.contains_spin(spin_name=spin_name1, spin_num=spin_num1, res_name=res_name1, res_num=res_num1, mol=mol_name1) or domain.contains_spin(spin_name=spin_name2, spin_num=spin_num2, res_name=res_name2, res_num=res_num2, mol=mol_name2):
            interatom.select = boolean_select(current=interatom.select, boolean=boolean)

        # Deselect containers outside of the domain.
        elif change_all:
            interatom.select = False


def sel_interatom(spin_id1=None, spin_id2=None, boolean='OR', change_all=False):
    """Select specific interatomic data containers.

    @keyword spin_id1:              The spin ID string of the first spin of the pair.
    @type spin_id1:                 str or None
    @keyword spin_id2:              The spin ID string of the second spin of the pair.
    @type spin_id2:                 str or None
    @param boolean:                 The boolean operator used to select the spin systems with.  It can be one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'.  This will be ignored if the change_all flag is set.
    @type boolean:                  str
    @keyword change_all:            A flag which if True will cause all spins not specified in the file to be deselected.  Only the boolean operator 'OR' is compatible with this flag set to True (all others will be ignored).
    @type change_all:               bool
    @raises RelaxNoSequenceError:   If no molecule/residue/spins sequence data exists.
    @raises RelaxError:             If the boolean operator is unknown.
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # First deselect all interatom containers if the change_all flag is set.
    if change_all:
        # Interatomic data loop.
        for interatom in interatomic_loop(skip_desel=False):
            interatom.select = False

    # Interatomic data loop.
    for interatom in interatomic_loop(selection1=spin_id1, selection2=spin_id2, skip_desel=False):
        # Select just the specified containers.
        if change_all:
            interatom.select = True

        # Boolean selections.
        else:
            interatom.select = boolean_select(current=interatom.select, boolean=boolean)


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
    check_pipe()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # First deselect all spins if the change_all flag is set.
    if change_all:
        # Loop over all spins.
        for spin in spin_loop():
            spin.select = False

    # Then deselect the spins in the file.
    ids = []
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
            spin.select = boolean_select(current=spin.select, boolean=boolean)

        # Store the spin ID for printouts.
        if spin.select:
            ids.append(id)

    # Printout.
    if not len(ids):
        print("No spins selected.")
    else:
        print("The following spins were selected:")
        for id in ids:
            print(id)


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
    check_pipe()

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
            spin.select = boolean_select(current=spin.select, boolean=boolean)
