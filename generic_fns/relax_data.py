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
"""Module for the manipulation of relaxation data."""

# Python module imports.
from copy import deepcopy
from numpy import array, float64, int32, ones, zeros
import string
import sys
from warnings import warn

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from data.exp_info import ExpInfo
from generic_fns import bmrb
from generic_fns.mol_res_spin import create_spin, exists_mol_res_spin_data, find_index, generate_spin_id, get_molecule_names, return_spin, spin_index_loop, spin_loop
from generic_fns import pipes
from generic_fns import value
from physical_constants import element_from_isotope, number_from_isotope
from relax_errors import RelaxError, RelaxNoRiError, RelaxNoSequenceError, RelaxNoSpinError, RelaxRiError
from relax_io import read_spin_data
from relax_warnings import RelaxWarning
import specific_fns


def back_calc(ri_id=None, ri_type=None, frq=None):
    """Back calculate the relaxation data.

    If no relaxation data currently exists, then the ri_id, ri_type, and frq args are required.


    @keyword ri_id:     The relaxation data ID string.  If not given, all relaxation data will be back calculated.
    @type ri_id:        None or str
    @keyword ri_type:   The relaxation data type.  This should be one of 'R1', 'R2', or 'NOE'.
    @type ri_type:      None or str
    @keyword frq:       The spectrometer proton frequency in Hz.
    @type frq:          None or float
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Initialise the global data for the current pipe if necessary.
    if not hasattr(cdp, 'frq'):
        cdp.frq = {}
    if not hasattr(cdp, 'ri_type'):
        cdp.ri_type = {}
    if not hasattr(cdp, 'ri_ids'):
        cdp.ri_ids = []

    # Update the global data if needed.
    if ri_id and ri_id not in cdp.ri_ids:
        cdp.ri_ids.append(ri_id)
        cdp.ri_type[ri_id] = ri_type
        cdp.frq[ri_id] = frq

    # Specific Ri back-calculate function setup.
    back_calculate = specific_fns.setup.get_specific_fn('back_calc_ri', pipes.get_type())

    # Loop over the spins.
    for spin, spin_id in spin_loop(return_id=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # The global index.
        spin_index = find_index(spin_id)

        # Initialise the spin data if necessary.
        if not hasattr(cdp, 'ri_data_bc'):
            spin.ri_data_bc = {}

        # Back-calculate the relaxation value.
        spin.ri_data_bc[ri_id] = back_calculate(spin_index=spin_index, ri_id=ri_id, ri_type=ri_type, frq=frq)


def bmrb_read(star, sample_conditions=None):
    """Read the relaxation data from the NMR-STAR dictionary object.

    @param star:                The NMR-STAR dictionary object.
    @type star:                 NMR_STAR instance
    @keyword sample_conditions: The sample condition label to read.  Only one sample condition can be read per data pipe.
    @type sample_conditions:    None or str
    """

    # Get the relaxation data.
    for data in star.relaxation.loop():
        # Store the keys.
        keys = data.keys()

        # Sample conditions do not match (remove the $ sign).
        if 'sample_cond_list_label' in keys and sample_conditions and string.replace(data['sample_cond_list_label'], '$', '') != sample_conditions:
            continue

        # Create the labels.
        ri_type = data['data_type']
        frq = float(data['frq']) * 1e6

        # Round the label to the nearest factor of 10.
        frq_label = str(int(round(float(data['frq'])/10)*10))

        # The ID string.
        ri_id = "%s_%s" % (ri_type, frq_label)

        # The number of spins.
        N = bmrb.num_spins(data)

        # No data in the saveframe.
        if N == 0:
            continue

        # The molecule names.
        mol_names = bmrb.molecule_names(data, N)

        # Generate the sequence if needed.
        bmrb.generate_sequence(N, spin_names=data['atom_names'], res_nums=data['res_nums'], res_names=data['res_names'], mol_names=mol_names)

        # The data and error.
        vals = data['data']
        errors = data['errors']
        if vals == None:
            vals = [None] * N
        if errors == None:
            errors = [None] * N

        # Data transformation.
        if vals != None and 'units' in keys:
            # Scaling.
            if data['units'] == 'ms':
                # Loop over the data.
                for i in range(N):
                    # The value.
                    if vals[i] != None:
                        vals[i] = vals[i] / 1000

                    # The error.
                    if errors[i] != None:
                        errors[i] = errors[i] / 1000

            # Invert.
            if data['units'] in ['s', 'ms']:
                # Loop over the data.
                for i in range(len(vals)):
                    # The value.
                    if vals[i] != None:
                        vals[i] = 1.0 / vals[i]

                    # The error.
                    if vals[i] != None and errors[i] != None:
                        errors[i] = errors[i] * vals[i]**2

        # Pack the data.
        pack_data(ri_id, ri_type, frq, vals, errors, mol_names=mol_names, res_nums=data['res_nums'], res_names=data['res_names'], spin_nums=None, spin_names=data['atom_names'], gen_seq=True)


def bmrb_write(star):
    """Generate the relaxation data saveframes for the NMR-STAR dictionary object.

    @param star:    The NMR-STAR dictionary object.
    @type star:     NMR_STAR instance
    """

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Initialise the spin specific data lists.
    mol_name_list = []
    res_num_list = []
    res_name_list = []
    atom_name_list = []
    isotope_list = []
    element_list = []
    attached_atom_name_list = []
    attached_isotope_list = []
    attached_element_list = []
    ri_data_list = []
    ri_data_err_list = []
    for i in range(cdp.num_ri):
        ri_data_list.append([])
        ri_data_err_list.append([])

    # Relax data labels.
    labels = cdp.ri_ids
    exp_label = []
    spectro_ids = []
    spectro_labels = []

    # Store the spin specific data in lists for later use.
    for spin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Skip spins with no relaxation data.
        if not hasattr(spin, 'ri_data'):
            continue

        # Check the data for None (not allowed in BMRB!).
        if res_num == None:
            raise RelaxError("For the BMRB, the residue of spin '%s' must be numbered." % spin_id)
        if res_name == None:
            raise RelaxError("For the BMRB, the residue of spin '%s' must be named." % spin_id)
        if spin.name == None:
            raise RelaxError("For the BMRB, the spin '%s' must be named." % spin_id)
        if spin.heteronuc_type == None:
            raise RelaxError("For the BMRB, the spin isotope type of '%s' must be specified." % spin_id)

        # The molecule/residue/spin info.
        mol_name_list.append(mol_name)
        res_num_list.append(str(res_num))
        res_name_list.append(str(res_name))
        atom_name_list.append(str(spin.name))

        # The attached atom info.
        if hasattr(spin, 'attached_atom'):
            attached_atom_name_list.append(str(spin.attached_atom))
        else:
            attached_atom_name_list.append(str(spin.attached_proton))
        attached_element_list.append(element_from_isotope(spin.proton_type))
        attached_isotope_list.append(str(number_from_isotope(spin.proton_type)))

        # The relaxation data.
        used_index = -ones(spin.num_ri)
        for i in range(len(cdp.ri_ids)):
            # Data exists.
            if cdp.ri_ids[i] in spin.ri_data.keys():
                ri_data_list[i].append(str(spin.ri_data[i]))
                ri_data_err_list[i].append(str(spin.ri_data_err[i]))
            else:
                ri_data_list[i].append(None)
                ri_data_err_list[i].append(None)

        # Other info.
        isotope_list.append(int(string.strip(spin.heteronuc_type, string.ascii_letters)))
        element_list.append(spin.element)

    # Convert the molecule names into the entity IDs.
    entity_ids = zeros(len(mol_name_list), int32)
    mol_names = get_molecule_names()
    for i in range(len(mol_name_list)):
        for j in range(len(mol_names)):
            if mol_name_list[i] == mol_names[j]:
                entity_ids[i] = j+1

    # Check the temperature control methods.
    if not hasattr(cdp, 'exp_info') or not hasattr(cdp.exp_info, 'temp_calibration'):
        raise RelaxError("The temperature calibration methods have not been specified.")
    if not hasattr(cdp, 'exp_info') or not hasattr(cdp.exp_info, 'temp_control'):
        raise RelaxError("The temperature control methods have not been specified.")

    # Check the peak intensity type.
    if not hasattr(cdp, 'exp_info') or not hasattr(cdp.exp_info, 'peak_intensity_type'):
        raise RelaxError("The peak intensity types measured for the relaxation data have not been specified.")

    # Loop over the relaxation data.
    for i in range(cdp.num_ri):
        # Alias.
        ri_id = cdp.ri_ids[i]
        ri_type = cdp.ri_type[ri_id]

        # Convert to MHz.
        frq = cdp.frq[ri_id] * 1e-6

        # Get the temperature control methods.
        temp_calib = cdp.exp_info.temp_calibration[ri_id]
        temp_control = cdp.exp_info.temp_control[ri_id]

        # Get the peak intensity type.
        peak_intensity_type = cdp.exp_info.peak_intensity_type[ri_id]

        # Check.
        if not temp_calib:
            raise RelaxError("The temperature calibration method for the '%s' relaxation data ID string has not been specified." % ri_id)
        if not temp_control:
            raise RelaxError("The temperature control method for the '%s' relaxation data ID string has not been specified." % ri_id)

        # Add the relaxation data.
        star.relaxation.add(data_type=ri_type, frq=frq, entity_ids=entity_ids, res_nums=res_num_list, res_names=res_name_list, atom_names=atom_name_list, atom_types=element_list, isotope=isotope_list, entity_ids_2=entity_ids, res_nums_2=res_num_list, res_names_2=res_name_list, atom_names_2=attached_atom_name_list, atom_types_2=attached_element_list, isotope_2=attached_isotope_list, data=ri_data_list[i], errors=ri_data_err_list[i], temp_calibration=temp_calib, temp_control=temp_control, peak_intensity_type=peak_intensity_type)

        # The experimental label.
        if ri_type == 'NOE':
            exp_name = 'steady-state NOE'
        else:
            exp_name = ri_type
        exp_label.append("%s MHz %s" % (frq, exp_name))

        # Spectrometer info.
        spectro_ids.append(cdp.remap_table[i] + 1)
        spectro_labels.append("$spectrometer_%s" % spectro_ids[-1])

    # Add the spectrometer info.
    for i in range(cdp.num_frq):
        star.nmr_spectrometer.add(name="$spectrometer_%s" % (i+1), manufacturer=None, model=None, frq=int(cdp.frq[i]/1e6))

    # Add the experiment saveframe.
    star.experiment.add(name=exp_label, spectrometer_ids=spectro_ids, spectrometer_labels=spectro_labels)


def copy(pipe_from=None, pipe_to=None, ri_id=None):
    """Copy the relaxation data from one data pipe to another.

    @keyword pipe_from: The data pipe to copy the relaxation data from.  This defaults to the current data pipe.
    @type pipe_from:    str
    @keyword pipe_to:   The data pipe to copy the relaxation data to.  This defaults to the current data pipe.
    @type pipe_to:      str
    @param ri_id:       The relaxation data ID string.
    @type ri_label:     str
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

    # Get the data pipes.
    dp_from = pipes.get_pipe(pipe_from)
    dp_to = pipes.get_pipe(pipe_to)

    # Test if pipe_from contains sequence data.
    if not exists_mol_res_spin_data(pipe_from):
        raise RelaxNoSequenceError

    # Test if pipe_to contains sequence data.
    if not exists_mol_res_spin_data(pipe_to):
        raise RelaxNoSequenceError

    # Test if relaxation data ID string exists for pipe_from.
    if ri_id and (not hasattr(dp_from, 'ri_ids') or ri_id not in dp_from.ri_ids):
        raise RelaxNoRiError(ri_id)

    # The IDs.
    if ri_id == None:
        ri_ids = dp_from.ri_ids
    else:
        ri_ids = [ri_id]

    # Init target pipe global structures.
    if not hasattr(dp_to, 'ri_ids'):
        dp_to.ri_ids = []
    if not hasattr(dp_to, 'ri_type'):
        dp_to.ri_type = {}
    if not hasattr(dp_to, 'frq'):
        dp_to.frq = {}

    # Loop over the Rx IDs.
    for ri_id in ri_ids:
        # Test if relaxation data ID string exists for pipe_to.
        if ri_id in dp_to.ri_ids:
            raise RelaxRiError(ri_id)

        # Copy the global data.
        dp_to.ri_ids.append(ri_id)
        dp_to.ri_type[ri_id] = dp_from.ri_type[ri_id]
        dp_to.frq[ri_id] = dp_from.frq[ri_id]

        # Spin loop.
        for mol_index, res_index, spin_index in spin_index_loop():
            # Alias the spin containers.
            spin_from = dp_from.mol[mol_index].res[res_index].spin[spin_index]
            spin_to = dp_to.mol[mol_index].res[res_index].spin[spin_index]

            # Initialise the spin data if necessary.
            if not hasattr(spin_to, 'ri_data'):
                spin_to.ri_data = {}
            if not hasattr(spin_to, 'ri_data_err'):
                spin_to.ri_data_err = {}

            # Copy the value and error from pipe_from.
            spin_to.ri_data[ri_id] = spin_from.ri_data[ri_id]
            spin_to.ri_data_err[ri_id] = spin_from.ri_data_err[ri_id]


def get_data_names(global_flag=False, sim_names=False):
    """Return a list of names of data structures associated with relaxation data.

    Description
    ===========

    The names are as follows:

    ri_data:  Relaxation data.

    ri_data_err:  Relaxation data error.

    ri_type:  The relaxation data type, i.e. one of ['NOE', 'R1', 'R2']

    frq:  NMR frequencies in Hz, eg [600.0 * 1e6, 500.0 * 1e6]


    @keyword global_flag:   A flag which if True corresponds to the pipe specific data structures and if False corresponds to the spin specific data structures.
    @type global_flag:      bool
    @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object names as well.
    @type sim_names:        bool
    @return:                The list of object names.
    @rtype:                 list of str
    """

    # Initialise.
    names = []

    # Global data names.
    if not sim_names and global_flag:
        names.append('ri_id')
        names.append('ri_type')
        names.append('frq')

    # Spin specific data names.
    if not sim_names and not global_flag:
        names.append('ri_data')
        names.append('ri_data_err')

    # Simulation object names.
    if sim_names and not global_flag:
        names.append('ri_data_sim')

    # Return the list of names.
    return names


def delete(ri_id=None):
    """Delete relaxation data corresponding to the relaxation data ID.

    @keyword ri_id: The relaxation data ID string.
    @type ri_id:    str
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data exists.
    if not hasattr(cdp, 'ri_ids') or ri_id not in cdp.ri_ids:
        raise RelaxNoRiError(ri_id)

    # Loop over the spins.
    for spin in spin_loop():
        # Relaxation data and errors.
        del spin.ri_data[ri_id]
        del spin.ri_data_err[ri_id]


def display(ri_id=None):
    """Display relaxation data corresponding to the ID.

    @keyword ri_id: The relaxation data ID string.
    @type ri_id:    str
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data exists.
    if not hasattr(cdp, 'ri_ids') or ri_id not in cdp.ri_ids:
        raise RelaxNoRiError(ri_id)

    # Print the data.
    value.write_data(param=ri_id, file=sys.stdout, return_value=return_value)


def pack_data(ri_id, ri_type, frq, values, errors, spin_ids=None, mol_names=None, res_nums=None, res_names=None, spin_nums=None, spin_names=None, gen_seq=False):
    """Pack the relaxation data into the data pipe and spin containers.

    The values, errors, and spin_ids arguments must be lists of equal length or None.  Each element i corresponds to a unique spin.

    @param ri_id:           The relaxation data ID string.
    @type ri_id:            str
    @param ri_type:         The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_type:          str
    @param frq:             The spectrometer proton frequency in Hz.
    @type frq:              float
    @keyword values:        The relaxation data for each spin.
    @type values:           None or list of float or float array
    @keyword errors:        The relaxation data errors for each spin.
    @type errors:           None or list of float or float array
    @keyword spin_ids:      The list of spin ID strings.  If the other spin identifiers are given, i.e. mol_names, res_nums, res_names, spin_nums, and/or spin_names, then this argument is not necessary.
    @type spin_ids:         None or list of str
    @keyword mol_names:     The list of molecule names used for creating the spin IDs (if not given) or for generating the sequence data.
    @type mol_names:        None or list of str
    @keyword res_nums:      The list of residue numbers used for creating the spin IDs (if not given) or for generating the sequence data.
    @type res_nums:         None or list of str
    @keyword res_names:     The list of residue names used for creating the spin IDs (if not given) or for generating the sequence data.
    @type res_names:        None or list of str
    @keyword spin_nums:     The list of spin numbers used for creating the spin IDs (if not given) or for generating the sequence data.
    @type spin_nums:        None or list of str
    @keyword spin_names:    The list of spin names used for creating the spin IDs (if not given) or for generating the sequence data.
    @type spin_names:       None or list of str
    @keyword gen_seq:       A flag which if True will cause the molecule, residue, and spin sequence data to be generated.
    @type gen_seq:          bool
    """

    # The number of spins.
    N = len(values)

    # Test the data.
    if errors != None and len(errors) != N:
        raise RelaxError("The length of the errors arg (%s) does not match that of the value arg (%s)." % (len(errors), N))
    if spin_ids and len(spin_ids) != N:
        raise RelaxError("The length of the spin ID strings arg (%s) does not match that of the value arg (%s)." % (len(mol_names), N))
    if mol_names and len(mol_names) != N:
        raise RelaxError("The length of the molecule names arg (%s) does not match that of the value arg (%s)." % (len(mol_names), N))
    if res_nums and len(res_nums) != N:
        raise RelaxError("The length of the residue numbers arg (%s) does not match that of the value arg (%s)." % (len(res_nums), N))
    if res_names and len(res_names) != N:
        raise RelaxError("The length of the residue names arg (%s) does not match that of the value arg (%s)." % (len(res_names), N))
    if spin_nums and len(spin_nums) != N:
        raise RelaxError("The length of the spin numbers arg (%s) does not match that of the value arg (%s)." % (len(spin_nums), N))
    if spin_names and len(spin_names) != N:
        raise RelaxError("The length of the spin names arg (%s) does not match that of the value arg (%s)." % (len(spin_names), N))

    # Generate some empty lists.
    if not mol_names:
        mol_names = [None] * N
    if not res_nums:
        res_nums = [None] * N
    if not res_names:
        res_names = [None] * N
    if not spin_nums:
        spin_nums = [None] * N
    if not spin_names:
        spin_names = [None] * N
    if errors == None:
        errors = [None] * N

    # Generate the spin IDs.
    if not spin_ids:
        spin_ids = []
        for i in range(N):
            spin_ids.append(generate_spin_id(spin_num=spin_nums[i], spin_name=spin_names[i], res_num=res_nums[i], res_name=res_names[i], mol_name=mol_names[i]))

    # Initialise the global data for the current pipe if necessary.
    if not hasattr(cdp, 'frq'):
        cdp.frq = {}
    if not hasattr(cdp, 'ri_type'):
        cdp.ri_type = {}
    if not hasattr(cdp, 'ri_ids'):
        cdp.ri_ids = []

    # Update the global data.
    cdp.ri_ids.append(ri_id)
    cdp.ri_type[ri_id] = ri_type
    cdp.frq[ri_id] = frq

    # Generate the sequence.
    if gen_seq:
        bmrb.generate_sequence(N, spin_ids=spin_ids, spin_nums=spin_nums, spin_names=spin_names, res_nums=res_nums, res_names=res_names, mol_names=mol_names)

    # Loop over the spin data.
    for i in range(N):
        # Get the corresponding spin container.
        spin = return_spin(spin_ids[i])
        if spin == None:
            raise RelaxNoSpinError(spin_ids[i])

        # Initialise the spin data if necessary.
        if not hasattr(spin, 'ri_data') or spin.ri_data == None:
            spin.ri_data = {}
        if not hasattr(spin, 'ri_data_err') or spin.ri_data_err == None:
            spin.ri_data_err = {}

        # Update all data structures.
        spin.ri_data[ri_id] = values[i]
        spin.ri_data_err[ri_id] = errors[i]


def peak_intensity_type(ri_id=None, type=None):
    """Set the type of intensity measured for the peaks.

    @keyword ri_id: The relaxation data ID string.
    @type ri_id:    str
    @keyword type:  The peak intensity type, one of 'height' or 'volume'.
    @type type:     str
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data exists.
    if not hasattr(cdp, 'ri_ids') or ri_id not in cdp.ri_ids:
        raise RelaxNoRiError(ri_id)

    # Check the values, and warn if not in the list.
    valid = ['height', 'volume']
    if type not in valid:
        raise RelaxError("The '%s' peak intensity type is unknown.  Please select one of %s." % (type, valid))

    # Set up the experimental info data container, if needed.
    if not hasattr(cdp, 'exp_info'):
        cdp.exp_info = ExpInfo()

    # Store the type.
    cdp.exp_info.setup_peak_intensity_type(ri_id, type)


def read(ri_id=None, ri_type=None, frq=None, file=None, dir=None, file_data=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None, spin_id=None):
    """Read R1, R2, or NOE relaxation data from a file.

    @param ri_id:           The relaxation data ID string.
    @type ri_id:            str
    @param ri_type:         The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_type:          str
    @param frq:             The spectrometer proton frequency in Hz.
    @type frq:              float
    @param file:            The name of the file to open.
    @type file:             str
    @param dir:             The directory containing the file (defaults to the current directory if None).
    @type dir:              str or None
    @param file_data:       An alternative opening a file, if the data already exists in the correct format.  The format is a list of lists where the first index corresponds to the row and the second the column.
    @type file_data:        list of lists
    @keyword spin_id_col:   The column containing the spin ID strings.  If supplied, the mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col arguments must be none.
    @type spin_id_col:      int or None
    @keyword mol_name_col:  The column containing the molecule name information.  If supplied, spin_id_col must be None.
    @type mol_name_col:     int or None
    @keyword res_name_col:  The column containing the residue name information.  If supplied, spin_id_col must be None.
    @type res_name_col:     int or None
    @keyword res_num_col:   The column containing the residue number information.  If supplied, spin_id_col must be None.
    @type res_num_col:      int or None
    @keyword spin_name_col: The column containing the spin name information.  If supplied, spin_id_col must be None.
    @type spin_name_col:    int or None
    @keyword spin_num_col:  The column containing the spin number information.  If supplied, spin_id_col must be None.
    @type spin_num_col:     int or None
    @keyword data_col:      The column containing the relaxation data.
    @type data_col:         int or None
    @keyword error_col:     The column containing the relaxation data errors.
    @type error_col:        int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword spin_id:       The spin ID string used to restrict data loading to a subset of all spins.
    @type spin_id:          None or str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if the ri_id already exists.
    if hasattr(cdp, 'ri_ids') and ri_id in cdp.ri_ids:
        raise RelaxError("The relaxation ID string '%s' already exists." % ri_id)

    # Loop over the file data to create the data structures for packing.
    values = []
    errors = []
    ids = []
    for data in read_spin_data(file=file, dir=dir, file_data=file_data, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep, spin_id=spin_id):
        # Unpack.
        if data_col and error_col:
            id, value, error = data
        elif data_col:
            id, value = data
            error = None
        else:
            id, error = data
            value = None

        # Pack the spin ID info.
        ids.append(id)

        # Convert the data.
        values.append(value)
        errors.append(error)

    # Pack the data.
    pack_data(ri_id, ri_type, frq, values, errors, ids)


def return_data_desc(name):
    """Return a description of the spin specific object.

    @param name:    The name of the spin specific object.
    @type name:     str
    """

    if name == 'ri_data':
        return 'The relaxation data'
    if name == 'ri_data_err':
        return 'The relaxation data errors'


def return_value(spin, data_type):
    """Return the value and error corresponding to 'data_type'.

    @param spin:        The spin container.
    @type spin:         SpinContainer instance
    @param data_type:   The relaxation data ID string.
    @type data_type:    str
    """

    # Relaxation data.
    data = None
    if hasattr(spin, 'ri_data') and spin.ri_data != None and data_type in spin.ri_data.keys():
        data = spin.ri_data[data_type]

    # Relaxation errors.
    error = None
    if hasattr(spin, 'ri_data_err') and spin.ri_data_err != None and data_type in spin.ri_data_err.keys():
        error = spin.ri_data_err[data_type]

    # Return the data.
    return data, error


def temp_calibration(ri_id=None, method=None):
    """Set the temperature calibration method.

    @keyword ri_id:     The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_id:        str
    @keyword method:    The temperature calibration method.
    @type method:       str
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data exists.
    if not hasattr(cdp, 'ri_ids') or ri_id not in cdp.ri_ids:
        raise RelaxNoRiError(ri_id)

    # Check the values, and warn if not in the list.
    valid = ['methanol', 'monoethylene glycol', 'no calibration applied']
    if method not in valid:
        warn(RelaxWarning("The '%s' method is unknown.  Please try to use one of %s." % (method, valid)))

    # Set up the experimental info data container, if needed.
    if not hasattr(cdp, 'exp_info'):
        cdp.exp_info = ExpInfo()

    # Store the method.
    cdp.exp_info.temp_calibration_setup(ri_id, method)


def temp_control(ri_id=None, method=None):
    """Set the temperature control method.

    @keyword ri_id:     The relaxation data ID string.
    @type ri_id:        str
    @keyword method:    The temperature control method.
    @type method:       str
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data exists.
    if not hasattr(cdp, 'ri_ids') or ri_id not in cdp.ri_ids:
        raise RelaxNoRiError(ri_id)

    # Check the values, and warn if not in the list.
    valid = ['single scan interleaving', 'temperature compensation block', 'single scan interleaving and temperature compensation block', 'single fid interleaving', 'single experiment interleaving', 'no temperature control applied']
    if method not in valid:
        raise RelaxError("The '%s' method is unknown.  Please select one of %s." % (method, valid))

    # Set up the experimental info data container, if needed.
    if not hasattr(cdp, 'exp_info'):
        cdp.exp_info = ExpInfo()

    # Store the method.
    cdp.exp_info.temp_control_setup(ri_id, method)


def update_data_structures_spin(spin=None, ri_label=None, frq_label=None, frq=None, value=None, error=None):
    """Update all relaxation data structures of the given spin container.

    @param spin:            The SpinContainer object.
    @type spin:             class instance
    @param ri_label:        The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:         str
    @param frq_label:       The field strength label.
    @type frq_label:        str
    @param frq:             The spectrometer proton frequency in Hz.
    @type frq:              float
    @param value:           The relaxation data value.
    @type value:            float
    @param error:           The relaxation data error.
    @type error:            float
    """

    # Initialise the relaxation data structures (if needed).
    data_init(spin, global_flag=False)

    # Find the index corresponding to 'ri_label' and 'frq_label'.
    index = find_ri_index(spin, ri_label, frq_label)

    # Append empty data.
    if index == None:
        spin.relax_data.append(None)
        spin.relax_error.append(None)
        spin.ri_labels.append(None)
        spin.remap_table.append(None)
        spin.noe_r1_table.append(None)

    # Set the index value.
    if index == None:
        i = len(spin.relax_data) - 1
    else:
        i = index

    # Relaxation data and errors.
    spin.relax_data[i] = value
    spin.relax_error[i] = error

    # Update the number of relaxation data points.
    if index == None:
        spin.num_ri = spin.num_ri + 1

    # Add ri_label to the data types.
    spin.ri_labels[i] = ri_label

    # Find if the frequency frq has already been loaded.
    remap = len(spin.frq)
    flag = 0
    for j in xrange(len(spin.frq)):
        if frq == spin.frq[j]:
            remap = j
            flag = 1

    # Update the remap table.
    spin.remap_table[i] = remap

    # Update the data structures which have a length equal to the number of field strengths.
    if not flag:
        # Update the number of frequencies.
        if index == None:
            spin.num_frq = spin.num_frq + 1

        # Update the frequency labels.
        spin.frq_labels.append(frq_label)

        # Update the frequency array.
        spin.frq.append(frq)

    # Update the NOE R1 translation table.
    # If the data corresponds to 'NOE', try to find if the corresponding R1 data.
    if ri_label == 'NOE':
        for j in xrange(spin.num_ri):
            if spin.ri_labels[j] == 'R1' and frq_label == spin.frq_labels[spin.remap_table[j]]:
                spin.noe_r1_table[spin.num_ri - 1] = j

    # Update the NOE R1 translation table.
    # If the data corresponds to 'R1', try to find if the corresponding NOE data.
    if ri_label == 'R1':
        for j in xrange(spin.num_ri):
            if spin.ri_labels[j] == 'NOE' and frq_label == spin.frq_labels[spin.remap_table[j]]:
                spin.noe_r1_table[j] = spin.num_ri - 1


def write(ri_id=None, file=None, dir=None, force=False):
    """Write relaxation data to a file.

    @keyword ri_id: The relaxation data ID string.
    @type ri_label: str
    @keyword file:  The name of the file to create.
    @type file:     str
    @keyword dir:   The directory to write to.
    @type dir:      str or None
    @keyword force: A flag which if True will cause any pre-existing file to be overwritten.
    @type force:    bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data exists.
    if not hasattr(cdp, 'ri_ids') or ri_id not in cdp.ri_ids:
        raise RelaxNoRiError(ri_id)

    # Create the file name if none is given.
    if file == None:
        file = ri_id + ".out"

    # Write the data.
    value.write(param=ri_id, file=file, dir=dir, force=force, return_value=return_value)
