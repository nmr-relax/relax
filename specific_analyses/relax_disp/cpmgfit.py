###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Functions for interfacing with Art Palmer's CPMGFit program."""

# Dependencies.
import dep_check

# Python module imports.
from math import pi
from os import F_OK, access, chmod, sep
from string import lower
PIPE, Popen = None, None
if dep_check.subprocess_module:
    from subprocess import PIPE, Popen
import sys

# relax module imports.
from lib.errors import RelaxError, RelaxDirError, RelaxFileError, RelaxNoSequenceError
from lib.io import mkdir_nofail, open_write_file, test_binary
from lib.physical_constants import g1H
from pipe_control import pipes
from pipe_control.spectrometer import get_frequencies
from pipe_control.mol_res_spin import exists_mol_res_spin_data, spin_loop
from specific_analyses.relax_disp.disp_data import loop_frq_point, return_param_key_from_data


def cpmgfit_execute(dir=None, binary='cpmgfit', force=False):
    """Execute CPMGFit for each spin input file.

    @keyword dir:       The directory where the input files are located.  If None, this defaults to the dispersion model name in lowercase.
    @type dir:          str or None
    @keyword binary:    The name of the CPMGFit binary file.  This can include the path to the binary.
    @type binary:       str
    @keyword force:     A flag which if True will cause any pre-existing files to be overwritten by CPMGFit.
    @type force:        bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if the experiment type has been set.
    if not hasattr(cdp, 'exp_type'):
        raise RelaxError("The relaxation dispersion experiment type has not been specified.")

    # Test if the model has been set.
    if not hasattr(cdp, 'model'):
        raise RelaxError("The relaxation dispersion model has not been specified.")

    # Translate the model.
    function = translate_model()

    # The directory.
    if dir == None:
        dir = lower(cdp.model)
    if not access(dir, F_OK):
        raise RelaxDirError('CPMGFit', dir)

    # Loop over each spin.
    for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
        # The spin input file name.
        file_in = dir + sep + spin_file_name(spin_id=spin_id)
        if not access(file_in, F_OK):
            raise RelaxFileError("spin input", file_in)

        # The spin output file name.
        file_out = dir + sep + spin_file_name(spin_id=spin_id, output=True)

        # Test the binary file string corresponds to a valid executable.
        test_binary(binary)

        # Execute CPMGFit.
        cmd = "%s -grid -xmgr -f %s | tee %s\n" % (binary, file_in, file_out)
        print("\n\n%s" % cmd)
        pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

        # Close the pipe.
        pipe.stdin.close()

        # Write to stdout.
        for line in pipe.stdout.readlines():
            # Decode Python 3 byte arrays.
            if hasattr(line, 'decode'):
                line = line.decode()

            # Write.
            sys.stdout.write(line)

        # Write to stderr.
        for line in pipe.stderr.readlines():
            # Decode Python 3 byte arrays.
            if hasattr(line, 'decode'):
                line = line.decode()

            # Write.
            sys.stderr.write(line)


def cpmgfit_input(dir=None, binary='cpmgfit', spin_id=None, force=False):
    """Create the CPMGFit input files.

    @keyword dir:               The optional directory to place the files into.  If None, then the files will be placed into a directory named after the dispersion model.
    @type dir:                  str or None
    @keyword binary:            The name of the CPMGFit binary file.  This can include the path to the binary.
    @type binary:               str
    @keyword spin_id:           The spin ID string to restrict the file creation to.
    @type spin_id:              str
    @keyword force:             A flag which if True will cause all pre-existing files to be overwritten.
    @type force:                bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if the experiment type has been set.
    if not hasattr(cdp, 'exp_type'):
        raise RelaxError("The relaxation dispersion experiment type has not been specified.")

    # Test if the model has been set.
    if not hasattr(cdp, 'model'):
        raise RelaxError("The relaxation dispersion model has not been specified.")

    # Translate the model.
    function = translate_model()

    # Directory creation.
    if dir == None:
        dir = lower(cdp.model)
    mkdir_nofail(dir, verbosity=0)

    # The 'run.sh' script.
    batch = open_write_file('batch_run.sh', dir, force)
    batch.write("#! /bin/sh\n\n")

    # Generate the input files for each spin.
    for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
        file_name = create_spin_input(function=function, spin=spin, spin_id=spin_id, dir=dir)

        # Add the file to the batch script.
        batch.write("%s -xmgr -f %s\n" % (binary, file_name))

    # Close the batch script, then make it executable.
    batch.close()
    chmod(dir + sep + 'batch_run.sh', 0755)


def create_spin_input(function=None, spin=None, spin_id=None, dir=None):
    """Generate the CPMGFit file for the given spin.

    @keyword function:  The CPMGFit model or function name.
    @type function:     str
    @keyword spin:      The spin container to generate the input file for.
    @type spin:         SpinContainer instance
    @keyword spin_id:   The spin ID string corresponding to the spin container.
    @type spin_id:      str
    @keyword dir:       The directory to place the file into.
    @type dir:          str or None
    @return:            The name of the file created.
    @rtype:             str
    """

    # The output file.
    file_name = spin_file_name(spin_id=spin_id)
    file = open_write_file(file_name=file_name, dir=dir, force=True)

    # The title.
    file.write("title %s\n" % spin_id)

    # The proton frequencies.
    frq = get_frequencies(units='T')

    # The frequency info.
    file.write("fields %s" % len(frq))
    for i in range(len(frq)):
        file.write(" %s" % frq[i])
    file.write("\n")

    # The function and parameters.
    if function == 'CPMG':
        # Function.
        file.write("function CPMG\n")

        # Parameters.
        file.write("R2 1 10 20\n")
        file.write("Rex 0 100.0 100\n")
        file.write("tex 0 10.0 100\n")

    # The function and parameters.
    elif function == 'Full_CPMG':
        # Function.
        file.write("function Full_CPMG\n")

        # Parameters.
        file.write("R2 1 10 20\n")
        file.write("papb 0.01 0.49 20\n")
        file.write("dw 0 10.0 100\n")
        file.write("kex 0.1 1.0 100\n")

    # The Grace setup.
    file.write("xmgr\n")
    file.write("@ xaxis label \"1/tcp (1/ms)\"\n")
    file.write("@ yaxis label \"R2(tcp) (rad/s)\"\n")
    file.write("@ xaxis ticklabel format decimal\n")
    file.write("@ yaxis ticklabel format decimal\n")
    file.write("@ xaxis ticklabel char size 0.8\n")
    file.write("@ yaxis ticklabel char size 0.8\n")
    file.write("@ world xmin 0.0\n")

    # The data.
    file.write("data\n")
    for frq, point in loop_frq_point():
        # The parameter key.
        param_key = return_param_key_from_data(frq=frq, point=point)

        # No data.
        if param_key not in spin.r2eff:
            continue

        # Tesla units.
        B0 = frq * 2.0 * pi / g1H

        # Write out the data and error.
        file.write("%-20f %-20f %-20f %-20f\n" % (point/1000.0, spin.r2eff[param_key], spin.r2eff_err[param_key], B0))

    # Close the file and return its name.
    file.close()
    return file_name


def spin_file_name(spin_id=None, output=False):
    """Generate the unique file name for the given spin ID.

    @keyword spin_id:   The spin ID string.
    @type spin_id:      str
    @keyword output:    A flag which if True will cause the CPMGFit output rather than input name to be returned.
    @return:            The file name.
    @rtype:             str
    """

    # Construct the name.
    name = "spin_%s." % spin_id
    if output:
        name += "out"
    else:
        name += "in"

    # Return the file name.
    return name


def translate_model():
    """Translate the dispersion model from relax notation to CPMGFit notation.

    @return:    The CPMGFit model name.
    @rtype:     str
    """

    # A translation table (relax to CPMGFit models).
    translation = {
        'LM63': 'CPMG',
        'CR72': 'Full_CPMG'
    }

    # No translation, so fail.
    if cdp.model not in translation:
        raise RelaxError("The conversion of the relax model '%s' to a CPMGFit model is not supported." % cdp.model)

    # Printout.
    print("Translating the relax '%s' model to the CPMGFit '%s' model." % (cdp.model, translation[cdp.model]))

    # Return the translated name.
    return translation[cdp.model]
