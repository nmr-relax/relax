###############################################################################
#                                                                             #
# Copyright (C) 2001-2009,2011-2012,2017 Edward d'Auvergne                    #
# Copyright (C) 2008 Sebastien Morin                                          #
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
"""Module for interfacing with Art Palmer's Modelfree 4 program."""


# Dependencies.
import dep_check

# Python module imports.
from math import pi
from os import F_OK, access, chdir, chmod, getcwd, listdir, remove, sep, system
from re import match, search
import signal
from stat import S_IRWXU, S_IRGRP, S_IROTH
PIPE, Popen = None, None
if dep_check.subprocess_module:
    from subprocess import PIPE, Popen
import sys

# relax module imports.
from lib.errors import RelaxError, RelaxDirError, RelaxFileError, RelaxNoInteratomError, RelaxNoModelError, RelaxNoPdbError, RelaxNoSequenceError, RelaxNoTensorError
from lib.io import mkdir_nofail, open_write_file, test_binary
from lib.periodic_table import periodic_table
from pipe_control import diffusion_tensor, pipes
from pipe_control.interatomic import return_interatom_list
from pipe_control.mol_res_spin import exists_mol_res_spin_data, spin_loop
from pipe_control.pipes import check_pipe
from specific_analyses.model_free.model import determine_model_type


def __deselect_spins():
    """Deselect spins with no or too little data, that are overfitting, etc."""

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Is structural data required?
    need_vect = False
    if hasattr(cdp, 'diff_tensor') and (cdp.diff_tensor.type == 'spheroid' or cdp.diff_tensor.type == 'ellipsoid'):
        need_vect = True

    # Loop over the sequence.
    for spin in spin_loop():
        # Relaxation data and errors must exist!
        if (not hasattr(spin, 'ri_data') or spin.ri_data == None) or (not hasattr(spin, 'ri_data_err') or spin.ri_data_err == None):
            spin.select = False

        # Require 3 or more relaxation data points.
        elif len(spin.ri_data) < 3:
            spin.select = False

        # Require at least as many data points as params to prevent over-fitting.
        elif hasattr(spin, 'params') and spin.params and len(spin.params) > len(spin.ri_data):
            spin.select = False


def create(dir=None, binary=None, diff_search=None, sims=None, sim_type=None, trim=None, steps=None, heteronuc_type=None, atom1=None, atom2=None, spin_id=None, force=False, constraints=True):
    """Create the Modelfree4 input files.

    The following files are created:
        - dir/mfin
        - dir/mfdata
        - dir/mfpar
        - dir/mfmodel
        - dir/run.sh

    @keyword dir:               The optional directory to place the files into.  If None, then the files will be placed into a directory named after the current data pipe.
    @type dir:                  str or None
    @keyword binary:            The name of the Modelfree4 binary file.  This can include the path to the binary.
    @type binary:               str
    @keyword diff_search:       The diffusion tensor search algorithm (see the Modelfree4 manual for details).
    @type diff_search:          str
    @keyword sims:              The number of Monte Carlo simulations to perform.
    @type sims:                 int
    @keyword sim_type:          The type of simulation to perform (see the Modelfree4 manual for details).
    @type sim_type:             str
    @keyword trim:              Trimming of the Monte Carlo simulations (see the Modelfree4 manual for details).
    @type trim:                 int
    @keyword steps:             The grid search size (see the Modelfree4 manual for details).
    @type steps:                int
    @keyword heteronuc_type:    The Modelfree4 three letter code for the heteronucleus type, e.g. '15N', '13C', etc.
    @type heteronuc_type:       str
    @keyword atom1:             The name of the heteronucleus in the PDB file.
    @type atom1:                str
    @keyword atom2:             The name of the proton in the PDB file.
    @type atom2:                str
    @keyword spin_id:           The spin identification string.
    @type spin_id:              str
    @keyword force:             A flag which if True will cause all pre-existing files to be overwritten.
    @type force:                bool
    @keyword constraints:       A flag which if True will result in constrained optimisation.
    @type constraints:          bool
    """

    # Test if the current pipe exists.
    check_pipe()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if the PDB file is loaded (for the spheroid and ellipsoid).
    if hasattr(cdp, 'diff_tensor') and not cdp.diff_tensor.type == 'sphere' and not hasattr(cdp, 'structure'):
        raise RelaxNoPdbError

    # Deselect certain spins.
    __deselect_spins()

    # Directory creation.
    if dir == None:
        dir = pipes.cdp_name()
    mkdir_nofail(dir, verbosity=0)

    # Number of field strengths and values.
    frq = []
    for ri_id in cdp.ri_ids:
        # New frequency.
        if cdp.spectrometer_frq[ri_id] not in frq:
            frq.append(cdp.spectrometer_frq[ri_id])

    # The 'mfin' file.
    mfin = open_write_file('mfin', dir, force)
    create_mfin(mfin, diff_search=diff_search, sims=sims, sim_type=sim_type, trim=trim, num_frq=len(frq), frq=frq)
    mfin.close()

    # Open the 'mfdata', 'mfmodel', and 'mfpar' files.
    mfdata = open_write_file('mfdata', dir, force)
    mfmodel = open_write_file('mfmodel', dir, force)
    mfpar = open_write_file('mfpar', dir, force)

    # Loop over the sequence.
    for spin, mol_name, res_num, res_name, id in spin_loop(spin_id, full_info=True, return_id=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # The 'mfdata' file.
        if not create_mfdata(mfdata, spin=spin, spin_id=id, num_frq=len(frq), frq=frq):
            continue

        # The 'mfmodel' file.
        create_mfmodel(mfmodel, spin=spin, spin_id=id, steps=steps, constraints=constraints)

        # The 'mfpar' file.
        create_mfpar(mfpar, spin=spin, spin_id=id, res_num=res_num, atom1=atom1, atom2=atom2)

    # Close the 'mfdata', 'mfmodel', and 'mfpar' files.
    mfdata.close()
    mfmodel.close()
    mfpar.close()

    # The 'run.sh' script.
    run = open_write_file('run.sh', dir, force)
    create_run(run, binary=binary, dir=dir)
    run.close()
    chmod(dir + sep+'run.sh', S_IRWXU|S_IRGRP|S_IROTH)


def create_mfdata(file, spin=None, spin_id=None, num_frq=None, frq=None):
    """Create the Modelfree4 input file 'mfmodel'.

    @param file:        The writable file object.
    @type file:         file object
    @param spin:        The spin container.
    @type spin:         SpinContainer instance
    @param spin_id:     The spin identification string.
    @type spin_id       str
    @keyword num_frq:   The number of spectrometer frequencies relaxation data was collected at.
    @type num_frq:      int
    @keyword frq:       The spectrometer frequencies.
    @type frq:          list of float
    @return:            True if file data is written, False otherwise.
    @rtype:             bool
    """

    # Spin title.
    file.write("\nspin     " + spin_id + "\n")

    # Data written flag.
    written = False

    # Loop over the frequencies.
    for j in range(num_frq):
        # Set the data to None.
        r1, r2, noe = None, None, None

        # Loop over the relaxation data.
        for ri_id in cdp.ri_ids:
            # The frequency does not match.
            if frq[j] != cdp.spectrometer_frq[ri_id]:
                continue

            # Find the corresponding R1.
            if cdp.ri_type[ri_id] == 'R1':
                r1 = spin.ri_data[ri_id]
                r1_err = spin.ri_data_err[ri_id]

            # Find the corresponding R2.
            elif cdp.ri_type[ri_id] == 'R2':
                r2 = spin.ri_data[ri_id]
                r2_err = spin.ri_data_err[ri_id]

            # Find the corresponding NOE.
            elif cdp.ri_type[ri_id] == 'NOE':
                noe = spin.ri_data[ri_id]
                noe_err = spin.ri_data_err[ri_id]

        # Test if the R1 exists for this frequency, otherwise skip the data.
        if r1:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('R1', frq[j]*1e-6, r1, r1_err, 1))
        else:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('R1', frq[j]*1e-6, 0, 0, 0))

        # Test if the R2 exists for this frequency, otherwise skip the data.
        if r2:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('R2', frq[j]*1e-6, r2, r2_err, 1))
        else:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('R2', frq[j]*1e-6, 0, 0, 0))

        # Test if the NOE exists for this frequency, otherwise skip the data.
        if noe:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('NOE', frq[j]*1e-6, noe, noe_err, 1))
        else:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('NOE', frq[j]*1e-6, 0, 0, 0))

        written = True

    return written


def create_mfin(file, diff_search=None, sims=None, sim_type=None, trim=None, num_frq=None, frq=None):
    """Create the Modelfree4 input file 'mfin'.

    @param file:            The writable file object.
    @type file:             file object
    @keyword diff_search:   The diffusion tensor search algorithm (see the Modelfree4 manual for
                            details).
    @type diff_search:      str
    @keyword sims:          The number of Monte Carlo simulations to perform.
    @type sims:             int
    @keyword sim_type:      The type of simulation to perform (see the Modelfree4 manual for
                            details).
    @type sim_type:         str
    @keyword trim:          Trimming of the Monte Carlo simulations (see the Modelfree4 manual for
                            details).
    @type trim:             int
    @keyword num_frq:       The number of spectrometer frequencies relaxation data was collected at.
    @type num_frq:          int
    @keyword frq:           The spectrometer frequencies.
    @type frq:              list of float
    """

    # Check for the diffusion tensor.
    if not hasattr(cdp, 'diff_tensor'):
        raise RelaxNoTensorError('diffusion')

    # Set the diffusion tensor specific values.
    if cdp.diff_tensor.type == 'sphere':
        diff = 'isotropic'
        algorithm = 'brent'
        tm = cdp.diff_tensor.tm / 1e-9
        dratio = 1
        theta = 0
        phi = 0
    elif cdp.diff_tensor.type == 'spheroid':
        diff = 'axial'
        algorithm = 'powell'
        tm = cdp.diff_tensor.tm / 1e-9
        dratio = cdp.diff_tensor.Dratio
        theta = cdp.diff_tensor.theta * 360.0 / (2.0 * pi)
        phi = cdp.diff_tensor.phi * 360.0 / (2.0 * pi)
    elif cdp.diff_tensor.type == 'ellipsoid':
        diff = 'anisotropic'
        algorithm = 'powell'
        tm = cdp.diff_tensor.tm / 1e-9
        dratio = 0
        theta = 0
        phi = 0

    # Add the main options.
    file.write("optimization    tval\n\n")
    file.write("seed            0\n\n")
    file.write("search          grid\n\n")

    # Diffusion type.
    if cdp.diff_tensor.fixed:
        algorithm = 'fix'

    file.write("diffusion       " + diff + " " + diff_search + "\n\n")
    file.write("algorithm       " + algorithm + "\n\n")

    # Monte Carlo simulations.
    if sims:
        file.write("simulations     " + sim_type + "    " + repr(sims) + "       " + repr(trim) + "\n\n")
    else:
        file.write("simulations     none\n\n")

    selection = 'none'    # To be changed.
    file.write("selection       " + selection + "\n\n")
    file.write("sim_algorithm   " + algorithm + "\n\n")

    file.write("fields          " + repr(num_frq))
    for val in frq:
        file.write("  " + repr(val*1e-6))
    file.write("\n")

    # tm.
    file.write('%-7s' % 'tm')
    file.write('%14.3f' % tm)
    file.write('%2i' % 1)
    file.write('%3i' % 0)
    file.write('%5i' % 5)
    file.write('%6i' % 15)
    file.write('%4i\n' % 20)

    # dratio.
    file.write('%-7s' % 'Dratio')
    file.write('%14s' % dratio)
    file.write('%2i' % 1)
    file.write('%3i' % 0)
    file.write('%5i' % 0)
    file.write('%6i' % 2)
    file.write('%4i\n' % 5)

    # theta.
    file.write('%-7s' % 'Theta')
    file.write('%14s' % theta)
    file.write('%2i' % 1)
    file.write('%3i' % 0)
    file.write('%5i' % 0)
    file.write('%6i' % 180)
    file.write('%4i\n' % 10)

    # phi.
    file.write('%-7s' % 'Phi')
    file.write('%14s' % phi)
    file.write('%2i' % 1)
    file.write('%3i' % 0)
    file.write('%5i' % 0)
    file.write('%6i' % 360)
    file.write('%4i\n' % 10)


def create_mfmodel(file, spin=None, spin_id=None, steps=None, constraints=None):
    """Create the Modelfree4 input file 'mfmodel'.

    @param file:            The writable file object.
    @type file:             file object
    @keyword spin:          The spin container.
    @type spin:             SpinContainer instance
    @keyword spin_id:       The spin identification string.
    @type spin_id           str
    @keyword steps:         The grid search size (see the Modelfree4 manual for details).
    @type steps:            int
    @keyword constraints:   A flag which if True will result in constrained optimisation.
    @type constraints:      bool
    """

    # Spin title.
    file.write("\nspin     " + spin_id + "\n")

    # tloc.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'tloc', 0))
    if 'tm' in spin.params:
        file.write('%-4i' % 1)
    else:
        file.write('%-4i' % 0)

    if constraints:
        file.write('%-2i' % 2)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 20, steps))

    # Theta.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'Theta', 0))
    file.write('%-4i' % 0)

    if constraints:
        file.write('%-2i' % 2)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 90, steps))

    # S2f.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'Sf2', 1))
    if 's2f' in spin.params:
        file.write('%-4i' % 1)
    else:
        file.write('%-4i' % 0)

    if constraints:
        file.write('%-2i' % 2)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 1, steps))

    # S2s.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'Ss2', 1))
    if 's2s' in spin.params or 's2' in spin.params:
        file.write('%-4i' % 1)
    else:
        file.write('%-4i' % 0)

    if constraints:
        file.write('%-2i' % 2)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 1, steps))

    # te.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'te', 0))
    if 'te' in spin.params or 'ts' in spin.params:
        file.write('%-4i' % 1)
    else:
        file.write('%-4i' % 0)

    if constraints:
        file.write('%-2i' % 2)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 10000, steps))

    # Rex.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'rex', 0))
    if 'rex' in spin.params:
        file.write('%-4i' % 1)
    else:
        file.write('%-4i' % 0)

    if constraints:
        file.write('%-2i' % -1)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 20, steps))


def create_mfpar(file, spin=None, spin_id=None, res_num=None, atom1=None, atom2=None):
    """Create the Modelfree4 input file 'mfpar'.

    @param file:        The writable file object.
    @type file:         file object
    @keyword spin:      The spin container.
    @type spin:         SpinContainer instance
    @keyword spin_id:   The spin identification string.
    @type spin_id       str
    @keyword res_num:   The residue number from the PDB file corresponding to the spin.
    @type res_num:      int
    @keyword atom1:     The name of the heteronucleus in the PDB file.
    @type atom1:        str
    @keyword atom2:     The name of the proton in the PDB file.
    @type atom2:        str
    """

    # Get the interatomic data containers.
    interatoms = return_interatom_list(spin_hash=spin._hash)
    if len(interatoms) == 0:
        raise RelaxNoInteratomError
    elif len(interatoms) > 1:
        raise RelaxError("Only one interatomic data container, hence dipole-dipole interaction, is supported per spin.")

    # Spin title.
    file.write("\nspin     " + spin_id + "\n")

    file.write('%-14s' % "constants")
    file.write('%-6i' % res_num)
    file.write('%-7s' % spin.isotope)
    file.write('%-8.4f' % (periodic_table.gyromagnetic_ratio(spin.isotope) / 1e7))
    file.write('%-8.3f' % (interatoms[0].r * 1e10))
    file.write('%-8.3f\n' % (spin.csa * 1e6))

    file.write('%-10s' % "vector")
    file.write('%-4s' % atom1)
    file.write('%-4s\n' % atom2)


def create_run(file, binary=None, dir=None):
    """Create the script 'run.sh' for the execution of Modelfree4.

    @param file:        The writable file object.
    @type file:         file object
    @keyword binary:    The name of the Modelfree4 binary file.  This can include the path to the
                        binary.
    @type binary:       str
    @keyword dir:       The directory to copy the PDB file to.
    @type dir:          str
    """

    # Check for the diffusion tensor.
    if not hasattr(cdp, 'diff_tensor'):
        raise RelaxNoTensorError('diffusion')

    file.write("#! /bin/sh\n")
    file.write(binary + " -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out")
    if cdp.diff_tensor.type != 'sphere':
        # Copy the first pdb file to the model directory so there are no problems with the existance of *.rotate files.
        mol = cdp.structure.structural_data[0].mol[0]
        system('cp ' + mol.file_path + sep + mol.file_name + ' ' + dir)
        file.write(" -s " + mol.file_name)
    file.write("\n")


def execute(dir, force, binary):
    """Execute Modelfree4.

    BUG:  Control-C during execution causes the cwd to stay as dir.


    @param dir:     The optional directory where the script is located.
    @type dir:      str or None
    @param force:   A flag which if True will cause any pre-existing files to be overwritten by
                    Modelfree4.
    @type force:    bool
    @param binary:  The name of the Modelfree4 binary file.  This can include the path to the
                    binary.
    @type binary:   str
    """

    # Check for the diffusion tensor.
    if not hasattr(cdp, 'diff_tensor'):
        raise RelaxNoTensorError('diffusion')

    # The current directory.
    orig_dir = getcwd()

    # The directory.
    if dir == None:
        dir = pipes.cdp_name()
    if not access(dir, F_OK):
        raise RelaxDirError('Modelfree4', dir)

    # Change to this directory.
    chdir(dir)

    # Catch failures and return to the correct directory.
    try:
        # Python 2.3 and earlier.
        if Popen == None:
            raise RelaxError("The subprocess module is not available in this version of Python.")

        # Test if the 'mfin' input file exists.
        if not access('mfin', F_OK):
            raise RelaxFileError('mfin input', 'mfin')

        # Test if the 'mfdata' input file exists.
        if not access('mfdata', F_OK):
            raise RelaxFileError('mfdata input', 'mfdata')

        # Test if the 'mfmodel' input file exists.
        if not access('mfmodel', F_OK):
            raise RelaxFileError('mfmodel input', 'mfmodel')

        # Test if the 'mfpar' input file exists.
        if not access('mfpar', F_OK):
            raise RelaxFileError('mfpar input', 'mfpar')

        # Test if the 'PDB' input file exists.
        if cdp.diff_tensor.type != 'sphere':
            pdb = cdp.structure.structural_data[0].mol[0].file_name
            if not access(pdb, F_OK):
                raise RelaxFileError('PDB', pdb)
        else:
            pdb = None

        # Remove the file 'mfout' and '*.out' if the force flag is set.
        if force:
            for file in listdir(getcwd()):
                if search('out$', file) or search('rotate$', file):
                    remove(file)

        # Test the binary file string corresponds to a valid executable.
        test_binary(binary)

        # Execute Modelfree4.
        if pdb:
            cmd = binary + ' -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out -s ' + pdb
        else:
            cmd = binary + ' -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out'
        pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)
        out, err = pipe.communicate()

        # Close the pipe.
        pipe.stdin.close()

        # Write to stdout.
        if out:
            # Decode Python 3 byte arrays.
            if hasattr(out, 'decode'):
                out = out.decode()

            # Write.
            sys.stdout.write(out)

        # Write to stderr.
        if err:
            # Decode Python 3 byte arrays.
            if hasattr(err, 'decode'):
                err = err.decode()

            # Write.
            sys.stderr.write(err)

        # Catch errors.
        if pipe.returncode == -signal.SIGSEGV:
            raise RelaxError("Modelfree4 return code 11 (Segmentation fault).\n")
        elif pipe.returncode:
            raise RelaxError("Modelfree4 return code %s.\n" % pipe.returncode)

    # Failure.
    except:
        # Change back to the original directory.
        chdir(orig_dir)

        # Reraise the error.
        raise

    # Change back to the original directory.
    chdir(orig_dir)


def extract(dir, spin_id=None):
    """Extract the Modelfree4 results out of the 'mfout' file.

    @param dir:         The directory containing the 'mfout' file.
    @type dir:          str or None
    @keyword spin_id:   The spin identification string.
    @type spin_id:      str or None
    """

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Check for the diffusion tensor.
    if not hasattr(cdp, 'diff_tensor'):
        raise RelaxNoTensorError('diffusion')

    # The directory.
    if dir == None:
        dir = pipes.cdp_name()
    if not access(dir, F_OK):
        raise RelaxDirError('Modelfree4', dir)

    # Test if the file exists.
    if not access(dir + sep+'mfout', F_OK):
        raise RelaxFileError('Modelfree4', dir + sep+'mfout')

    # Determine the parameter set.
    model_type = determine_model_type()

    # Open the file.
    mfout_file = open(dir + sep+'mfout', 'r')
    mfout_lines = mfout_file.readlines()
    mfout_file.close()

    # Get the section line positions of the mfout file.
    global_chi2_pos, diff_pos, s2_pos, s2f_pos, s2s_pos, te_pos, rex_pos, chi2_pos = line_positions(mfout_lines)

    # Find out if simulations were carried out.
    sims = 0
    for i in range(len(mfout_lines)):
        if search('_iterations', mfout_lines[i]):
            row = mfout_lines[i].split()
            sims = int(row[1])

    # Global data.
    if model_type in ['all', 'diff']:
        # Global chi-squared.
        row = mfout_lines[global_chi2_pos].split()
        cdp.chi2 = float(row[1])

        # Spherical diffusion tensor.
        if cdp.diff_tensor.type == 'sphere':
            # Split the lines.
            tm_row = mfout_lines[diff_pos].split()

            # Set the params.
            cdp.diff_tensor.set(param='tm', value=float(tm_row[2]))

        # Spheroid diffusion tensor.
        else:
            # Split the lines.
            tm_row = mfout_lines[diff_pos].split()
            dratio_row = mfout_lines[diff_pos+1].split()
            theta_row = mfout_lines[diff_pos+2].split()
            phi_row = mfout_lines[diff_pos+3].split()

            # Set the params.
            diffusion_tensor.set([float(tm_row[2]), float(dratio_row[2]), float(theta_row[2])*2.0*pi/360.0, float(phi_row[2])*2.0*pi/360.0], ['tm', 'Dratio', 'theta', 'phi'])

    # Loop over the sequence.
    pos = 0
    for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
        # Skip deselected residues.
        if not spin.select:
            continue

        # Get the residue number from the mfout file.
        mfout_res_num = int(mfout_lines[s2_pos + pos].split()[0])

        # Skip the spin if the residue doesn't match.
        if mfout_res_num != res_num:
            continue

        # Test that the model has been set (needed to differentiate between te and ts).
        if not hasattr(spin, 'model'):
            raise RelaxNoModelError

        # Get the S2 data.
        if 's2' in spin.params:
            spin.s2, spin.s2_err = get_mf_data(mfout_lines, s2_pos + pos)

        # Get the S2f data.
        if 's2f' in spin.params or 's2s' in spin.params:
            spin.s2f, spin.s2f_err = get_mf_data(mfout_lines, s2f_pos + pos)

        # Get the S2s data.
        if 's2f' in spin.params or 's2s' in spin.params:
            spin.s2s, spin.s2s_err = get_mf_data(mfout_lines, s2s_pos + pos)

        # Get the te data.
        if 'te' in spin.params:
            spin.te, spin.te_err = get_mf_data(mfout_lines, te_pos + pos)
            spin.te = spin.te / 1e12
            spin.te_err = spin.te_err / 1e12

        # Get the ts data.
        if 'ts' in spin.params:
            spin.ts, spin.ts_err = get_mf_data(mfout_lines, te_pos + pos)
            spin.ts = spin.ts / 1e12
            spin.ts_err = spin.ts_err / 1e12

        # Get the Rex data.
        if 'rex' in spin.params:
            spin.rex, spin.rex_err = get_mf_data(mfout_lines, rex_pos + pos)
            spin.rex = spin.rex / (2.0 * pi * cdp.spectrometer_frq[cdp.ri_ids[0]])**2
            spin.rex_err = spin.rex_err / (2.0 * pi * cdp.spectrometer_frq[cdp.ri_ids[0]])**2

        # Get the chi-squared data.
        if not sims:
            row = mfout_lines[chi2_pos + pos].split()
            spin.chi2 = float(row[1])
        else:
            # The mfout chi2 position (with no sims) plus 2 (for the extra XML) plus the residue position times 22 (because of the simulated SSE rows).
            row = mfout_lines[chi2_pos + 2 + 22*pos].split()
            spin.chi2 = float(row[1])

        # Increment the residue position.
        pos = pos + 1


def get_mf_data(mfout_lines, pos):
    """Extract the model-free data from the given position of the mfout file.

    This method is designed to catch a number of bugs in Modelfree4's mfout file.

    The first bug is the presence of a series of '*' characters causing a fusion of two columns.
    This is handled by splitting by the '*' char and then returning the first element.

    The second bug is when the floating point number is too big to fit into Modelfree4's string
    format limit of 15.3f.  This results in a results line such as:

    246      10000.00019682363392.000    1          0.000          0.000          0.000          0.000

    This is caught by scanning for two '.' characters in the column, and handled by assuming
    that every floating point number will have three decimal characters.

    @param mfout_lines: A list of all the lines of the mfout file.
    @type mfout_lines:  list of str
    @param pos:         The mfout line position.
    @type pos:          int
    @return:            The value and error.
    @rtype:             tuple of 2 floats
    """

    # Split the line up.
    row = mfout_lines[pos].split()

    # The value and error, assuming a bug free mfout file.
    val = row[1]
    err = row[4]

    # The Modelfree4 '*' column fusion bug.
    if search(r'\*', val) or search(r'\*', err):
        # Split by the '*' character.
        val_row = val.split('*')
        err_row = err.split('*')

        # The value and error (the first elements).
        val = val_row[0]
        err = err_row[0]

    # The Modelfree4 large float column fusion bug.
    new_row = []
    fused = False
    for element in row:
        # Count the number of '.' characters.
        num = element.count('.')

        # Catch two or more '.' characters.
        if num > 1:
            # Set the fused flag.
            fused = True

            # Loop over each fused number.
            for i in range(num):
                # Find the index of the first '.'.
                index = element.find('.')

                # The first number (index + decimal point + 3 decimal chars).
                new_row.append(element[0:index+4])

                # Strip the first number from the element for the next loop iteration.
                element = element[index+4:]

        # Otherwise the column element is fine.
        else:
            new_row.append(element)

    # Bug has been caught.
    if fused:
        val = new_row[1]
        err = new_row[4]

    # Return the value and error, as floats.
    return float(val), float(err)


def line_positions(mfout_lines):
    """Function for getting the section positions (line number) of the mfout file.

    @param mfout_lines:     A list of all the lines of the mfout file.
    @type mfout_lines:      list of str
    @return:                The line indices where the s2, s2f, s2s, te, rex, and chi2 sections
                            start in the mfout file.
    @rtype:                 tuple of int
    """

    # Loop over the file.
    i = 0
    while i < len(mfout_lines):
        # Global chi2.
        if match('data_chi_square', mfout_lines[i]):
            global_chi2_pos = i + 1

        # Diffusion tensor.
        if match('data_diffusion_tensor', mfout_lines[i]):
            diff_pos = i + 3

        # Model-free data.
        if match('data_model_1', mfout_lines[i]):
            # Shift down two lines (to avoid the lines not starting with a space).
            i = i + 2

            # Walk through all the data.
            while True:
                # Break once the end of the data section is reached.
                if not mfout_lines[i] == '\n' and not search('^ ', mfout_lines[i]):
                    break

                # Split the line up.
                row = mfout_lines[i].split()

                # S2 position (skip the heading and move to the first residue).
                if len(row) == 2 and row[0] == 'S2':
                    s2_pos = i + 1

                # S2f position (skip the heading and move to the first residue).
                if len(row) == 2 and row[0] == 'S2f':
                    s2f_pos = i + 1

                # S2s position (skip the heading and move to the first residue).
                if len(row) == 2 and row[0] == 'S2s':
                    s2s_pos = i + 1

                # te position (skip the heading and move to the first residue).
                if len(row) == 2 and row[0] == 'te':
                    te_pos = i + 1

                # Rex position (skip the heading and move to the first residue).
                if len(row) == 2 and row[0] == 'Rex':
                    rex_pos = i + 1

                # Move to the next line number.
                i = i + 1

        # Chi-squared values.
        if match('data_sse', mfout_lines[i]):
            chi2_pos = i + 3

        # Move to the next line number.
        i = i + 1

    # Return the positions.
    return global_chi2_pos, diff_pos, s2_pos, s2f_pos, s2s_pos, te_pos, rex_pos, chi2_pos
