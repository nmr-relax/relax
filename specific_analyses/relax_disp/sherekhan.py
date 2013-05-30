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
"""Functions for interfacing with Adam Mazur's ShereKhan program."""

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
from lib.io import mkdir_nofail, open_write_file
from lib.physical_constants import g1H, g15N
from pipe_control import pipes
from pipe_control.spectrometer import get_frequencies
from pipe_control.mol_res_spin import exists_mol_res_spin_data, spin_loop
from specific_analyses.relax_disp.disp_data import loop_frq, loop_point, return_param_key_from_data


def sherekhan_input(dir=None, spin_id=None, force=False):
    """Create the ShereKhan input files.

    @keyword dir:               The optional directory to place the files into.  If None, then the files will be placed into a directory named after the dispersion model.
    @type dir:                  str or None
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

    # Test that this is a fixed time period experiment.
    if len(cdp.relax_time_list) != 1:
            raise RelaxError("ShereKhan only supports the fixed time relaxation dispersion experiments.")

    # Directory creation.
    if dir == None:
        dir = lower(cdp.model)
    mkdir_nofail(dir, verbosity=0)

    # Loop over the magnetic fields.
    frq_index = 0
    for frq in loop_frq():
        # The ShereKhan input file.
        file = open_write_file('sherekhan_%s.py' % (frq_index+1), dir, force)

        # The B0 field for the nuclei of interest in MHz.
        file.write("%s\n" % (frq / g1H * g15N / 1e6))

        # The constant relaxation time for the CPMG experiment in seconds.
        file.write("%s\n" % (cdp.relax_time_list[0]))

        # The comment line.#nu_cpmg(Hz) R2(1/s) Esd(R2))
        file.write("# %-18s %-20s %-20s\n" % ("nu_cpmg (Hz)", "R2eff (rad/s)", "Error"))

        # Generate the input files for each spin.
        for spin, mol_name, res_num, res_name, id in spin_loop(full_info=True, selection=spin_id, return_id=True, skip_desel=True):
            # Name the residue if needed.
            if res_name == None:
                res_name = 'X'

            # The residue ID line.
            file.write("# %s%s\n" % (res_name, res_num))

            # Loop over the dispersion points.
            for point in loop_point(skip_ref=True):
                # The parameter key.
                param_key = return_param_key_from_data(frq=frq, point=point)

                # No data.
                if param_key not in spin.r2eff:
                    continue

                # Write out the data.
                file.write("%20.15g %20.15g %20.15g\n" % (point, spin.r2eff[param_key], spin.r2eff_err[param_key]))

        # Close the file.
        file.close()

        # Increment the field index.
        frq_index += 1
