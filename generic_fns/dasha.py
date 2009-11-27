###############################################################################
#                                                                             #
# Copyright (C) 2005-2009 Edward d'Auvergne                                   #
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
"""Module for interfacing with Dasha."""

# Python module imports.
from math import pi
from os import F_OK, access, chdir, getcwd, popen3, sep
from string import lower
import sys

# relax module imports.
from generic_fns import angles, diffusion_tensor, pipes, value
from generic_fns.mol_res_spin import exists_mol_res_spin_data, first_residue_num, last_residue_num, residue_loop, spin_loop
from relax_errors import RelaxDirError, RelaxError, RelaxFileError, RelaxNoPdbError, RelaxNoSequenceError, RelaxNoTensorError
from relax_io import mkdir_nofail, open_write_file, test_binary
from specific_fns.setup import model_free_obj


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
        # Relaxation data must exist!
        if not hasattr(spin, 'relax_data'):
            spin.select = False

        # Require 3 or more relaxation data points.
        elif len(spin.relax_data) < 3:
            spin.select = False

        # Require at least as many data points as params to prevent over-fitting.
        elif hasattr(spin, 'params') and spin.params and len(spin.params) > len(spin.relax_data):
            spin.select = False


def create(algor='LM', dir=None, force=False):
    """Create the Dasha script file 'dasha_script' for controlling the program.

    @keyword algor: The optimisation algorithm to use.  This can be the Levenberg-Marquardt
                    algorithm 'LM' or the Newton-Raphson algorithm 'NR'.
    @type algor:    str
    @keyword dir:   The optional directory to place the script into.
    @type dir:      str or None
    @keyword force: A flag which if True will cause any pre-existing file to be overwritten.
    @type force:    bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Determine the parameter set.
    model_type = model_free_obj._determine_model_type()

    # Test if diffusion tensor data for the data_pipe exists.
    if model_type != 'local_tm' and not hasattr(cdp, 'diff_tensor'):
        raise RelaxNoTensorError('diffusion')

    # Test if the PDB file has been loaded (for the spheroid and ellipsoid).
    if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere' and not hasattr(cdp, 'structure'):
        raise RelaxNoPdbError

    # Test the optimisation algorithm.
    if algor not in ['LM', 'NR']:
        raise RelaxError("The Dasha optimisation algorithm " + repr(algor) + " is unknown, it should either be 'LM' or 'NR'.")

    # Multiple spins per residue not allowed.
    for residue in residue_loop():
        # Test the number of spins.
        if len(residue.spin) > 1:
            raise RelaxError("More than one spin per residue is not supported.")

    # Deselect certain spins.
    __deselect_spins()

    # Directory creation.
    if dir == None:
        dir = pipes.cdp_name()
    mkdir_nofail(dir, verbosity=0)

    # Number of field strengths and values.
    num_frq = 0
    frq = []
    for spin in spin_loop():
        if hasattr(spin, 'num_frq'):
            if spin.num_frq > num_frq:
                # Number of field strengths.
                num_frq = spin.num_frq

                # Field strength values.
                for val in spin.frq:
                    if val not in frq:
                        frq.append(val)

    # Calculate the angle alpha of the XH vector in the spheroid diffusion frame.
    if cdp.diff_tensor.type == 'spheroid':
        angles.spheroid_frame()

    # Calculate the angles theta and phi of the XH vector in the ellipsoid diffusion frame.
    elif cdp.diff_tensor.type == 'ellipsoid':
        angles.ellipsoid_frame()

    # The 'dasha_script' file.
    script = open_write_file(file_name='dasha_script', dir=dir, force=force)
    create_script(script, model_type, algor)
    script.close()


def create_script(file, model_type, algor):
    """Create the Dasha script file.

    @param file:        The opened file descriptor.
    @type file:         file object
    @param model_type:  The model-free model type.
    @type model_type:   str
    @param algor:       The optimisation algorithm to use.  This can be the Levenberg-Marquardt
                        algorithm 'LM' or the Newton-Raphson algorithm 'NR'.
    @type algor:        str
    """

    # Delete all data.
    file.write('# Delete all data.\n')
    file.write('del 1 10000\n')

    # Nucleus type.
    file.write('\n# Nucleus type.\n')
    nucleus = None
    for spin in spin_loop():
        # Can only handle one spin type.
        if nucleus and spin.heteronuc_type != nucleus:
            raise RelaxError("The nuclei '%s' and '%s' do not match, relax can only handle one nucleus type in Dasha." % (nucleus, spin.heteronuc_type))

        # Set the nucleus.
        if not nucleus:
            nucleus = spin.heteronuc_type

    # Convert the name and write it.
    if nucleus == '15N':
        nucleus = 'N15'
    elif nucleus == '13C':
        nucleus = 'C13'
    else:
        raise RelaxError('Cannot handle the nucleus type ' + repr(nucleus) + ' within Dasha.')
    file.write('set nucl ' + nucleus + '\n')

    # Number of frequencies.
    file.write('\n# Number of frequencies.\n')
    file.write('set n_freq ' + repr(cdp.num_frq) + '\n')

    # Frequency values.
    file.write('\n# Frequency values.\n')
    for i in xrange(cdp.num_frq):
        file.write('set H1_freq ' + repr(cdp.frq[i] / 1e6) + ' ' + repr(i+1) + '\n')

    # Set the diffusion tensor.
    file.write('\n# Set the diffusion tensor.\n')
    if model_type != 'local_tm':
        # Sphere.
        if cdp.diff_tensor.type == 'sphere':
            file.write('set tr ' + repr(cdp.diff_tensor.tm / 1e-9) + '\n')

        # Spheroid.
        elif cdp.diff_tensor.type == 'spheroid':
            file.write('set tr ' + repr(cdp.diff_tensor.tm / 1e-9) + '\n')

        # Ellipsoid.
        elif cdp.diff_tensor.type == 'ellipsoid':
            # Get the eigenvales.
            Dx, Dy, Dz = diffusion_tensor.return_eigenvalues()

            # Geometric parameters.
            file.write('set tr ' + repr(cdp.diff_tensor.tm / 1e-9) + '\n')
            file.write('set D1/D3 ' + repr(Dx / Dz) + '\n')
            file.write('set D2/D3 ' + repr(Dy / Dz) + '\n')

            # Orientational parameters.
            file.write('set alfa ' + repr(cdp.diff_tensor.alpha / (2.0 * pi) * 360.0) + '\n')
            file.write('set betta ' + repr(cdp.diff_tensor.beta / (2.0 * pi) * 360.0) + '\n')
            file.write('set gamma ' + repr(cdp.diff_tensor.gamma / (2.0 * pi) * 360.0) + '\n')

    # Reading the relaxation data.
    file.write('\n# Reading the relaxation data.\n')
    file.write('echo Reading the relaxation data.\n')
    noe_index = 1
    r1_index = 1
    r2_index = 1
    for i in xrange(cdp.num_ri):
        # NOE.
        if cdp.ri_labels[i] == 'NOE':
            # Data set number.
            number = noe_index

            # Data type.
            data_type = 'noe'

            # Increment the data set index.
            noe_index = noe_index + 1

        # R1.
        elif cdp.ri_labels[i] == 'R1':
            # Data set number.
            number = r1_index

            # Data type.
            data_type = '1/T1'

            # Increment the data set index.
            r1_index = r1_index + 1

        # R2.
        elif cdp.ri_labels[i] == 'R2':
            # Data set number.
            number = r2_index

            # Data type.
            data_type = '1/T2'

            # Increment the data set index.
            r2_index = r2_index + 1

        # Set the data type.
        if number == 1:
            file.write('\nread < ' + data_type + '\n')
        else:
            file.write('\nread < ' + data_type + ' ' + repr(number) + '\n')

        # The relaxation data.
        for residue in residue_loop():
            # Alias the spin.
            spin = residue.spin[0]

            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip and deselect spins for which relaxation data is missing.
            if len(spin.relax_data) != cdp.num_ri:
                spin.select = False
                continue

            # Data and errors.
            file.write(repr(residue.num) + ' ' + repr(spin.relax_data[i]) + ' ' + repr(spin.relax_error[i]) + '\n')

        # Terminate the reading.
        file.write('exit\n')

    # Individual residue optimisation.
    if model_type == 'mf':
        # Loop over the residues.
        for residue in residue_loop():
            # Alias the spin.
            spin = residue.spin[0]

            # Skip deselected spins.
            if not spin.select:
                continue

            # Comment.
            file.write('\n\n\n# Residue ' + repr(residue.num) + '\n\n')

            # Echo.
            file.write('echo Optimisation of residue ' + repr(residue.num) + '\n')

            # Select the spin.
            file.write('\n# Select the residue.\n')
            file.write('set cres ' + repr(residue.num) + '\n')

            # The angle alpha of the XH vector in the spheroid diffusion frame.
            if cdp.diff_tensor.type == 'spheroid':
                file.write('set teta ' + repr(spin.alpha) + '\n')

            # The angles theta and phi of the XH vector in the ellipsoid diffusion frame.
            elif cdp.diff_tensor.type == 'ellipsoid':
                file.write('\n# Setting the spherical angles of the XH vector in the ellipsoid diffusion frame.\n')
                file.write('set teta ' + repr(spin.theta) + '\n')
                file.write('set fi ' + repr(spin.phi) + '\n')

            # The 'jmode'.
            if 'ts' in spin.params:
                jmode = 3
            elif 'te' in spin.params:
                jmode = 2
            elif 'S2' in spin.params:
                jmode = 1

            # Chemical exchange.
            if 'Rex' in spin.params:
                exch = True
            else:
                exch = False

            # Anisotropic diffusion.
            if cdp.diff_tensor.type == 'sphere':
                anis = False
            else:
                anis = True

            # Axial symmetry.
            if cdp.diff_tensor.type == 'spheroid':
                sym = True
            else:
                sym = False

            # Set the jmode.
            file.write('\n# Set the jmode.\n')
            file.write('set def jmode ' + repr(jmode))
            if exch:
                file.write(' exch')
            if anis:
                file.write(' anis')
            if sym:
                file.write(' sym')
            file.write('\n')

            # Parameter default values.
            file.write('\n# Parameter default values.\n')
            file.write('reset jmode ' + repr(residue.num) + '\n')

            # Bond length.
            file.write('\n# Bond length.\n')
            file.write('set r_hx ' + repr(spin.r / 1e-10) + '\n')

            # CSA value.
            file.write('\n# CSA value.\n')
            file.write('set csa ' + repr(spin.csa / 1e-6) + '\n')

            # Fix the tf parameter if it isn't in the model.
            if not 'tf' in spin.params and jmode == 3:
                file.write('\n# Fix the tf parameter.\n')
                file.write('fix tf 0\n')

        # Optimisation of all residues.
        file.write('\n\n\n# Optimisation of all residues.\n')
        if algor == 'LM':
            file.write('lmin ' + repr(first_residue_num()) + ' ' + repr(last_residue_num()))
        elif algor == 'NR':
            file.write('min ' + repr(first_residue_num()) + ' ' + repr(last_residue_num()))

        # Show the results.
        file.write('\n# Show the results.\n')
        file.write('echo\n')
        file.write('show all\n')

        # Write the results.
        file.write('\n# Write the results.\n')
        file.write('write S2.out S\n')
        file.write('write S2f.out Sf\n')
        file.write('write S2s.out Ss\n')
        file.write('write te.out te\n')
        file.write('write tf.out tf\n')
        file.write('write ts.out ts\n')
        file.write('write Rex.out rex\n')
        file.write('write chi2.out F\n')

    else:
        raise RelaxError('Optimisation of the parameter set ' + repr(model_type) + ' currently not supported.')


def execute(dir, force, binary):
    """Execute Dasha.

    @param dir:     The optional directory where the script is located.
    @type dir:      str or None
    @param force:   A flag which if True will cause any pre-existing files to be overwritten by
                    Dasha.
    @type force:    bool
    @param binary:  The name of the Dasha binary file.  This can include the path to the binary.
    @type binary:   str
    """

    # Test the binary file string corresponds to a valid executable.
    test_binary(binary)

    # The current directory.
    orig_dir = getcwd()

    # The directory.
    if dir == None:
        dir = pipes.cdp_name()
    if not access(dir, F_OK):
        raise RelaxDirError('Dasha', dir)

    # Change to this directory.
    chdir(dir)

    # Catch failures and return to the correct directory.
    try:
        # Test if the 'dasha_script' script file exists.
        if not access('dasha_script', F_OK):
            raise RelaxFileError('dasha script', 'dasha_script')

        # Execute Dasha.
        stdin, stdout, stderr = popen3(binary)

        # Get the contents of the script and pump it into Dasha.
        script = open('dasha_script')
        lines = script.readlines()
        script.close()
        for line in lines:
            stdin.write(line)

        # Close the pipe.
        stdin.close()

        # Write to stdout and stderr.
        for line in stdout.readlines():
            sys.stdout.write(line)
        for line in stderr.readlines():
            sys.stderr.write(line)

    # Failure.
    except:
        # Change back to the original directory.
        chdir(orig_dir)

        # Reraise the error.
        raise

    # Change back to the original directory.
    chdir(orig_dir)

    # Print some blank lines (aesthetics)
    sys.stdout.write('\n\n')


def extract(dir):
    """Extract the data from the Dasha results files.

    @param dir:     The optional directory where the results file is located.
    @type dir:      str or None
    """

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # The directory.
    if dir == None:
        dir = pipes.cdp_name()
    if not access(dir, F_OK):
        raise RelaxDirError('Dasha', dir)

    # Loop over the parameters.
    for param in ['S2', 'S2f', 'S2s', 'te', 'tf', 'ts', 'Rex']:
        # The file name.
        file_name = dir + sep + param + '.out'

        # Test if the file exists.
        if not access(file_name, F_OK):
            raise RelaxFileError('Dasha', file_name)

        # Scaling.
        if param in ['te', 'tf', 'ts']:
            scaling = 1e-9
        elif param == 'Rex':
            scaling = 1.0 / (2.0 * pi * cdp.frq[0]) ** 2
        else:
            scaling = 1.0

        # Set the values.
        value.read(param=param, scaling=scaling, file=file_name, res_num_col=1, res_name_col=None, data_col=2, error_col=3)

        # Clean up of non-existant parameters (set the parameter to None!).
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip the spin (don't set the parameter to None) if the parameter exists in the model.
            if param in spin.params:
                continue

            # Set the parameter to None.
            setattr(spin, lower(param), None)

    # Extract the chi-squared values.
    file_name = dir + sep+'chi2.out'

    # Test if the file exists.
    if not access(file_name, F_OK):
        raise RelaxFileError('Dasha', file_name)

    # Set the values.
    value.read(param='chi2', file=file_name, res_num_col=1, res_name_col=None, data_col=2, error_col=3)
