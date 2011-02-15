###############################################################################
#                                                                             #
# Copyright (C) 2008-2011 Edward d'Auvergne                                   #
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
"""Module containing functions for BMRB support."""

# Python module imports.
from os import F_OK, access

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from data.exp_info import ExpInfo
import dep_check
from generic_fns import exp_info
from generic_fns.mol_res_spin import create_spin, generate_spin_id, return_residue, return_spin
from info import Info_box
from relax_errors import RelaxError, RelaxFileError, RelaxFileOverwriteError, RelaxNoModuleInstallError, RelaxNoPipeError
from relax_io import get_file_path, mkdir_nofail
import specific_fns
from version import version_full


def display(version='3.1'):
    """Display the results in the BMRB NMR-STAR format."""

    # Test if bmrblib is installed.
    if not dep_check.bmrblib_module:
        raise RelaxNoModuleInstallError('BMRB library', 'bmrblib')

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Specific results writing function.
    write_function = specific_fns.setup.get_specific_fn('bmrb_write', ds[ds.current_pipe].pipe_type, raise_error=False)

    # Write the results.
    write_function(sys.stdout, version=version)


def generate_sequence(N=0, spin_ids=None, spin_nums=None, spin_names=None, res_nums=None, res_names=None, mol_names=None):
    """Generate the sequence data from the BRMB information.

    @keyword N:             The number of spins.
    @type N:                int
    @keyword spin_ids:      The list of spin IDs.
    @type spin_ids:         list of str
    @keyword spin_nums:     The list of spin numbers.
    @type spin_nums:        list of int or None
    @keyword spin_names:    The list of spin names.
    @type spin_names:       list of str or None
    @keyword res_nums:      The list of residue numbers.
    @type res_nums:         list of int or None
    @keyword res_names:     The list of residue names.
    @type res_names:        list of str or None
    @keyword mol_names:     The list of molecule names.
    @type mol_names:        list of str or None
    """

    # The blank data.
    if not spin_nums:
        spin_nums = [None] * N
    if not spin_names:
        spin_names = [None] * N
    if not res_nums:
        res_nums = [None] * N
    if not res_names:
        res_names = [None] * N
    if not mol_names:
        mol_names = [None] * N

    # Generate the spin IDs.
    spin_ids = []
    for i in range(N):
        spin_ids.append(generate_spin_id(mol_name=mol_names[i], res_num=res_nums[i], spin_name=spin_names[i]))

    # Loop over the spin data.
    for i in range(N):
        # The spin already exists.
        spin = return_spin(spin_ids[i])
        if spin:
            continue

        # The residue container.
        if not mol_names:
            res_id = generate_spin_id(res_num=res_nums[i], res_name=res_names[i])
        else:
            res_id = generate_spin_id(mol_name=mol_names[i], res_num=res_nums[i], res_name=res_names[i])

        # The spin container needs to be named.
        res_cont = return_residue(res_id)
        if res_cont and len(res_cont.spin) == 1 and res_cont.spin[0].name == None and res_cont.spin[0].num == None:
            # Name and number the spin.
            res_cont.spin[0].name = spin_names[i]
            res_cont.spin[0].num = spin_nums[i]

            # Jump to the next spin.
            continue

        # Create the spin.
        create_spin(spin_num=spin_nums[i], spin_name=spin_names[i], res_num=res_nums[i], res_name=res_names[i], mol_name=mol_names[i])


def list_sample_conditions(star):
    """Get a listing of all the sample conditions.

    @param star:    The NMR-STAR dictionary object.
    @type star:     NMR_STAR instance
    @return:        The list of sample condition names.
    @rtype:         list of str
    """

    # Init.
    sample_conds = []

    # Get the sample conditions.
    for data in star.sample_conditions.loop():
        # Store the framecode.
        sample_conds.append(data['sf_framecode'])

    # Return the names.
    return sample_conds


def molecule_names(data, N=0):
    """Generate the molecule names list.

    @param data:    An element of data from bmrblib.
    @type data:     dict
    @return:        The list of molecule names.
    @rtype:         list of str
    """

    # The molecule index and name.
    mol_index = []
    for i in range(N):
        if 'entity_ids' in data.keys() and data['entity_ids'] != None and data['entity_ids'][i] != None:
            mol_index.append(int(data['entity_ids'][i]) -1 )
        else:
            mol_index = [0]*N
    mol_names = []
    for i in range(N):
        mol_names.append(cdp.mol[mol_index[i]].name)

    # Return the names.
    return mol_names


def num_spins(data):
    """Determine the number of spins in the given data.

    @param data:    An element of data from bmrblib.
    @type data:     dict
    @return:        The number of spins.
    @rtype:         int
    """

    # The number of spins.
    N = 0
    if 'data_ids' in data.keys() and data['data_ids']:
        N = len(data['data_ids'])
    elif 'entity_ids' in data.keys() and data['entity_ids']:
        N = len(data['entity_ids'])
    elif 'res_nums' in data.keys() and data['res_nums']:
        N = len(data['res_nums'])
    elif 's2' in data.keys() and data['s2']:
        N = len(data['s2'])

    # Return the number.
    return N


def read(file=None, directory=None, version=None, sample_conditions=None):
    """Read the contents of a BMRB NMR-STAR formatted file.

    @keyword file:              The name of the BMRB STAR formatted file.
    @type file:                 str
    @keyword directory:         The directory where the file is located.
    @type directory:            None or str
    @keyword version:           The BMRB version to force the reading.
    @type version:              None or str
    @keyword sample_conditions: The sample condition label to read.  Only one sample condition can be read per data pipe.
    @type sample_conditions:    None or str
    """

    # Test if bmrblib is installed.
    if not dep_check.bmrblib_module:
        raise RelaxNoModuleInstallError('BMRB library', 'bmrblib')

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Make sure that the data pipe is empty.
    if not ds[ds.current_pipe].is_empty():
        raise RelaxError("The current data pipe is not empty.")

    # Get the full file path.
    file_path = get_file_path(file_name=file, dir=directory)

    # Fail if the file does not exist.
    if not access(file_path, F_OK):
        raise RelaxFileError(file_path)

    # Specific results reading function.
    read_function = specific_fns.setup.get_specific_fn('bmrb_read', ds[ds.current_pipe].pipe_type)

    # Read the results.
    read_function(file_path, version=version, sample_conditions=sample_conditions)


def write(file=None, directory=None, version='3.1', force=False):
    """Create a BMRB NMR-STAR formatted file."""

    # Test if bmrblib is installed.
    if not dep_check.bmrblib_module:
        raise RelaxNoModuleInstallError('BMRB library', 'bmrblib')

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # The special data pipe name directory.
    if directory == 'pipe_name':
        directory = ds.current_pipe

    # Specific results writing function.
    write_function = specific_fns.setup.get_specific_fn('bmrb_write', ds[ds.current_pipe].pipe_type)

    # Get the full file path.
    file_path = get_file_path(file, directory)

    # Fail if the file already exists and the force flag is False.
    if access(file_path, F_OK) and not force:
        raise RelaxFileOverwriteError(file_path, 'force flag')

    # Print out.
    print("Opening the file '%s' for writing." % file_path)

    # Create the directories.
    mkdir_nofail(directory, verbosity=0)

    # Get the info box.
    info = Info_box()

    # Add the relax citations.
    for id, key in zip(['relax_ref1', 'relax_ref2'], ['dAuvergneGooley08a', 'dAuvergneGooley08b']):
        # Alias the bib entry.
        bib = info.bib[key]

        # Add.
        cdp.exp_info.add_citation(cite_id=id, authors=bib.author2, doi=bib.doi, pubmed_id=bib.pubmed_id, full_citation=bib.cite_short(doi=False, url=False), title=bib.title, status=bib.status, type=bib.type, journal_abbrev=bib.journal, journal_full=bib.journal_full, volume=bib.volume, issue=bib.number, page_first=bib.page_first, page_last=bib.page_last, year=bib.year)

    # Add the relax software package.
    cdp.exp_info.software_setup(name=exp_info.SOFTWARE['relax'].name, version=version_full(), vendor_name=exp_info.SOFTWARE['relax'].authors, url=exp_info.SOFTWARE['relax'].url, cite_ids=['relax_ref1', 'relax_ref2'], tasks=exp_info.SOFTWARE['relax'].tasks)

    # Execute the specific BMRB writing code.
    write_function(file_path, version=version)
