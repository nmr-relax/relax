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

# Module docstring.
"""Module for the manipulation of pseudocontact shift data."""

# Python module imports.
from copy import deepcopy
from numpy import float64, zeros
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import exists_mol_res_spin_data, generate_spin_id_data_array, return_spin, spin_index_loop, spin_loop
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoPdbError, RelaxNoResError, RelaxNoPCSError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoSpinError, RelaxPCSError
from relax_io import extract_data, strip


def add_data_to_spin(spin=None, ri_labels=None, remap_table=None, frq_labels=None, frq=None, values=None, errors=None, sim=False):
    """Add the relaxation data to the spin.

    @keyword spin:          The spin container.
    @type spin:             SpinContainer instance
    @keyword ri_labels:     The labels corresponding to the data type, eg ['NOE', 'R1', 'R2',
                            'NOE', 'R1', 'R2'].
    @type ri_labels:        list of str
    @keyword remap_table:   A translation table to map relaxation data points to their
                            frequencies, eg [0, 0, 0, 1, 1, 1].
    @type remap_table:      list of int
    @keyword frq_labels:    NMR frequency labels, eg ['600', '500'].
    @type frq_labels:       list of str
    @keyword frq:           NMR frequencies in Hz, eg [600.0 * 1e6, 500.0 * 1e6].
    @type frq:              list of float
    @keyword values:        The relaxation data.
    @type values:           list of float
    @keyword errors:        The relaxation errors.
    @type errors:           list of float
    @keyword sim:           A flag which if True means the data corresponds to Monte Carlo
                            simulation data.
    @type sim:              bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError


    # Global (non-spin specific) data.
    #####################################

    # Initialise the global data if necessary.
    data_init(cdp, global_flag=True)

    # Add the data structures.
    cdp.ri_labels = deepcopy(ri_labels)
    cdp.remap_table = deepcopy(remap_table)
    cdp.frq_labels = deepcopy(frq_labels)
    cdp.frq = deepcopy(frq)
    cdp.num_ri = len(ri_labels)
    cdp.num_frq = len(frq)

    # Update the NOE R1 translation table.
    update_noe_r1_table(cdp)


    # Spin specific data.
    #####################

    # Relaxation data.
    if not sim:
        # Initialise the relaxation data structures (if needed).
        data_init(spin, global_flag=False)

        # Relaxation data and errors.
        spin.relax_data = values
        spin.relax_error = errors

        # Associated data structures.
        spin.ri_labels = ri_labels
        spin.remap_table = remap_table

        # Remove any data with the value None.
        for index, Ri in enumerate(spin.relax_data):
            if Ri == None:
                spin.relax_data.pop(index)
                spin.relax_error.pop(index)
                spin.ri_labels.pop(index)
                spin.remap_table.pop(index)

        # Remove any data with error of None.
        for index,error in enumerate(spin.relax_error):
            if error == None:
                spin.relax_data.pop(index)
                spin.relax_error.pop(index)
                spin.ri_labels.pop(index)
                spin.remap_table.pop(index)

        # Associated data structures.
        spin.frq_labels = frq_labels
        spin.frq = frq
        spin.num_ri = len(ri_labels)
        spin.num_frq = len(frq)

        # Update the NOE R1 translation table.
        update_noe_r1_table(spin)

    # Simulation data.
    else:
        # Create the data structure if necessary.
        if not hasattr(spin, 'relax_sim_data') or type(spin.relax_sim_data) != list:
            spin.relax_sim_data = []

        # Append the simulation's relaxation data.
        spin.relax_sim_data.append(values)


def centre(atom_id=None, pipe=None):
    """Specify the atom in the loaded structure corresponding to the paramagnetic centre.

    @keyword atom_id:   The atom identification string.
    @type atom_id:      str
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the current data pipe.
    dp = pipes.get_pipe(pipe)

    # Test if the structure has been loaded.
    if not hasattr(dp, 'structure'):
        raise RelaxNoPdbError

    # Test the centre has already been set.
    if hasattr(dp, 'paramagnetic_centre'):
        raise RelaxError, "The paramagnetic centre has already been set to the coordinates " + `dp.paramagnetic_centre` + "."

    # Get the positions.
    pos = zeros(3, float64)
    i = 0
    for R in dp.structure.atom_loop(atom_id=atom_id, pos_flag=True):
        pos = pos + R
        i = i + 1

    # Averaging.
    pos = pos / float(i)

    # Print out.
    print "Paramagnetic centre located at: " + `pos`

    # Set the centre (place it into the current data pipe).
    cdp.paramagnetic_centre = pos


def copy(pipe_from=None, pipe_to=None, ri_label=None, frq_label=None):
    """Copy the relaxation data from one data pipe to another.

    @keyword pipe_from: The data pipe to copy the relaxation data from.  This defaults to the
                        current data pipe.
    @type pipe_from:    str
    @keyword pipe_to:   The data pipe to copy the relaxation data to.  This defaults to the current
                        data pipe.
    @type pipe_to:      str
    @param ri_label:    The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:     str
    @param frq_label:   The field strength label.
    @type frq_label:    str
    """

    # Defaults.
    if pipe_from == None and pipe_to == None:
        raise RelaxError, "The pipe_from and pipe_to arguments cannot both be set to None."
    elif pipe_from == None:
        pipe_from = pipes.cdp_name()
    elif pipe_to == None:
        pipe_to = pipes.cdp_name()

    # Test if the pipe_from and pipe_to data pipes exist.
    pipes.test(pipe_from)
    pipes.test(pipe_to)

    # Get the data pipes.
    dp_from = pipes.get_pipe(pipe_from)
    dp_to = pipes.get_pipe(pipe_to)

    # Test if pipe_from contains sequence data.
    if not exists_mol_res_spin_data(pipe_from):
        raise RelaxNoSequenceError

    # Test if pipe_to contains sequence data.
    if not exists_mol_res_spin_data(pipe_to):
        raise RelaxNoSequenceError

    # Copy all data.
    if ri_label == None and frq_label == None:
        # Get all data structure names.
        names = get_data_names()

        # Spin loop.
        for mol_index, res_index, spin_index in spin_index_loop():
            # Alias the spin containers.
            spin_from = dp_from.mol[mol_index].res[res_index].spin[spin_index]
            spin_to = dp_to.mol[mol_index].res[res_index].spin[spin_index]

            # Loop through the data structure names.
            for name in names:
                # Skip the data structure if it does not exist.
                if not hasattr(spin_from, name):
                    continue

                # Copy the data structure.
                setattr(spin_to, name, deepcopy(getattr(spin_from, name)))

    # Copy a specific data set.
    else:
        # Test if relaxation data corresponding to 'ri_label' and 'frq_label' exists for pipe_from.
        if not test_labels(ri_label, frq_label, pipe=pipe_from):
            raise RelaxNoRiError, (ri_label, frq_label)

        # Test if relaxation data corresponding to 'ri_label' and 'frq_label' exists for pipe_to.
        if not test_labels(ri_label, frq_label, pipe=pipe_to):
            raise RelaxRiError, (ri_label, frq_label)

        # Spin loop.
        for mol_index, res_index, spin_index in spin_index_loop():
            # Alias the spin containers.
            spin_from = dp_from.mol[mol_index].res[res_index].spin[spin_index]
            spin_to = dp_to.mol[mol_index].res[res_index].spin[spin_index]

            # Find the index corresponding to 'ri_label' and 'frq_label'.
            index = find_index(spin_from, ri_label, frq_label)

            # Catch any problems.
            if index == None:
                continue

            # Get the value and error from pipe_from.
            value = spin_from.relax_data[index]
            error = spin_from.relax_error[index]

            # Update all data structures for pipe_to.
            update_data_structures_spin(spin_to, ri_label, frq_label, frq, value, error)


def data_init(container, global_flag=False):
    """Function for initialising the data structures for a spin container.

    @param container:       The data pipe or spin data container (PipeContainer or SpinContainer).
    @type container:        class instance
    @keyword global_flag:   A flag which if True corresponds to the pipe specific data structures
                            and if False corresponds to the spin specific data structures.
    @type global_flag:      bool
    """

    # Get the data names.
    data_names = get_data_names(global_flag)

    # Init.
    list_data = [ 'relax_data',
                  'relax_error',
                  'ri_labels',
                  'remap_table',
                  'noe_r1_table',
                  'frq_labels',
                  'frq' ]
    zero_data = [ 'num_ri', 'num_frq' ]

    # Loop over the data structure names.
    for name in data_names:
        # If the name is not in the container, add it as an empty array.
        if name in list_data and not hasattr(container, name):
            setattr(container, name, [])

        # If the name is not in the container, add it as a variable set to zero.
        if name in zero_data and not hasattr(container, name):
            setattr(container, name, 0)


def get_data_names(global_flag=False, sim_names=False):
    """Return a list of names of data structures associated with relax_data.

    Description
    ===========

    The names are as follows:

    relax_data:  Relaxation data.

    relax_error:  Relaxation error.

    num_ri:  Number of data points, eg 6.

    num_frq:  Number of field strengths, eg 2.

    ri_labels:  Labels corresponding to the data type, eg ['NOE', 'R1', 'R2', 'NOE', 'R1',
    'R2'].

    remap_table:  A translation table to map relaxation data points to their frequencies, eg [0,
    0, 0, 1, 1, 1].

    noe_r1_table:  A translation table to direct the NOE data points to the R1 data points.
    This is used to speed up calculations by avoiding the recalculation of R1 values.  eg [None,
    None, 0, None, None, 3]

    frq_labels:  NMR frequency labels, eg ['600', '500']

    frq:  NMR frequencies in Hz, eg [600.0 * 1e6, 500.0 * 1e6]


    @keyword global_flag:   A flag which if True corresponds to the pipe specific data structures
                            and if False corresponds to the spin specific data structures.
    @type global_flag:      bool
    @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object names as
                            well.
    @type sim_names:        bool
    @return:                The list of object names.
    @rtype:                 list of str
    """

    # Initialise.
    names = []

    # Global data names.
    if not sim_names and global_flag:
        names.append('num_frq')
        names.append('frq')
        names.append('frq_labels')
        names.append('num_ri')
        names.append('ri_labels')
        names.append('remap_table')
        names.append('noe_r1_table')

    # Residue specific data names.
    if not sim_names and not global_flag:
        names.append('num_frq')
        names.append('frq')
        names.append('frq_labels')
        names.append('num_ri')
        names.append('ri_labels')
        names.append('remap_table')
        names.append('noe_r1_table')
        names.append('relax_data')
        names.append('relax_error')

    # Simulation object names.
    if sim_names and not global_flag:
        names.append('relax_sim_data')

    # Return the list of names.
    return names


def find_index(data, ri_label, frq_label):
    """Function for finding the index corresponding to ri_label and frq_label.

    @param data:        The class instance containing the ri_label and frq_label variables.
    @type data:         PipeContainer or SpinContainer
    @param ri_label:    The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:     str
    @param frq_label:   The field strength label.
    @type frq_label:    str
    @return:            The index corresponding to the relaxation data.  If there is no
                        relaxation data corresponding to the labels, None is returned.
    @rtype:             None or int
    """

    # No data.num_ri data structure.
    if not hasattr(data, 'num_ri'):
        return None

    # Initialise.
    index = None

    # Find the index.
    for j in xrange(data.num_ri):
        if ri_label == data.ri_labels[j] and frq_label == data.frq_labels[data.remap_table[j]]:
            index = j

    # Return the index.
    return index


def read(id=None, file=None, dir=None, file_data=None, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, data_col=2, error_col=3, sep=None):
    """Read the PCS data from file.

    @param id:              The alignment identification string.
    @type id:               str
    @param file:            The name of the file to open.
    @type file:             str
    @param dir:             The directory containing the file (defaults to the current directory
                            if None).
    @type dir:              str or None
    @param file_data:       An alternative opening a file, if the data already exists in the
                            correct format.  The format is a list of lists where the first index
                            corresponds to the row and the second the column.
    @type file_data:        list of lists
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
    @param sep:             The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Alias the current data pipe.
    cdp = pipes.get_pipe()

    # Test if PCS data corresponding to 'id' already exists.
    if data_col != None and hasattr(cdp, 'pcs_ids') and id in cdp.pcs_ids:
        raise RelaxPCSError, id

    # Either the data or error column must be supplied.
    if data_col == None and error_col == None:
        raise RelaxError, "One of either the data or error column must be supplied."

    # Minimum number of columns.
    min_col_num = max(mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col)

    # Extract the data from the file.
    if not file_data:
        # Extract.
        file_data = extract_data(file, dir)

        # Count the number of header lines.
        header_lines = 0
        for i in xrange(len(file_data)):
            try:
                if data_col != None:
                    float(file_data[i][data_col])
                else:
                    float(file_data[i][error_col])
            except:
                header_lines = header_lines + 1
            else:
                break

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip the data of all comments and empty lines.
        file_data = strip(file_data)

        # Test the validity of the PCS data.
        for i in xrange(len(file_data)):
            # Skip missing data.
            if len(file_data[i]) <= min_col_num:
                continue
            elif data_col != None and file_data[i][data_col] == 'None':
                continue
            elif error_col != None and file_data[i][error_col] == 'None':
                continue

            # Test that the data are numbers.
            try:
                if res_num_col != None:
                    int(file_data[i][res_num_col])
                if spin_num_col != None:
                    int(file_data[i][spin_num_col])
                if data_col != None:
                    float(file_data[i][data_col])
                if error_col != None:
                    float(file_data[i][error_col])
            except ValueError:
                raise RelaxError, "The PCS data in the line " + `file_data[i]` + " is invalid."


    # Global (non-spin specific) data.
    ##################################

    # Initialise.
    if not hasattr(cdp, 'pcs_ids'):
        cdp.pcs_ids = []

    # Add the PCS id string.
    if id not in cdp.pcs_ids:
        cdp.pcs_ids.append(id)


    # Spin specific data.
    #####################

    # Loop over the PCS data.
    for i in xrange(len(file_data)):
        # Skip missing data.
        if len(file_data[i]) <= min_col_num:
            continue

        # Generate the spin identification string.
        id = generate_spin_id_data_array(data=file_data[i], mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col)

        # Convert the data.
        value = None
        if data_col != None:
            value = eval(file_data[i][data_col])
        error = None
        if error_col != None:
            error = eval(file_data[i][error_col])

        # Test the error value (cannot be 0.0).
        if error == 0.0:
            raise RelaxError, "An invalid error value of zero has been encountered."

        # Get the corresponding spin container.
        spin = return_spin(id)
        if spin == None:
            raise RelaxNoSpinError, id

        # Add the data.
        if data_col != None:
            # Initialise.
            if not hasattr(spin, 'pcs'):
                spin.pcs = []

            # Append the value.
            spin.pcs.append(value)

        # Add the error.
        if error_col != None:
            # Initialise.
            if not hasattr(spin, 'pcs_err'):
                spin.pcs_err = []

            # Append the error.
            spin.pcs_err.append(error)


def return_data_desc(name):
    """Return a description of the spin specific object.

    @param name:    The name of the spin specific object.
    @type name:     str
    """

    if name == 'num_frq':
        return 'Number of spectrometer frequencies'
    if name == 'frq':
        return 'Frequencies'
    if name == 'frq_labels':
        return 'Frequency labels'
    if name == 'num_ri':
        return 'Number of relaxation data sets'
    if name == 'ri_labels':
        return 'Relaxation data set labels'
    if name == 'remap_table':
        return 'Table mapping frequencies to relaxation data'
    if name == 'noe_r1_table':
        return 'Table mapping the NOE to the corresponding R1'
    if name == 'relax_data':
        return 'The relaxation data'
    if name == 'relax_error':
        return 'The relaxation data errors'
