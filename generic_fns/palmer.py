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
"""Module for creating and processing input and output for Art Palmer's Modelfree 4 program."""


# Python module imports.
from math import pi
from os import F_OK, P_WAIT, access, chdir, chmod, getcwd, listdir, remove, system
from re import match, search
from string import count, find, split

# UNIX only functions from the os module (Modelfree4 only runs under UNIX anyway).
try:
    from os import spawnlp
except ImportError:
    pass

# relax module imports.
from data import Data as relax_data_store
from generic_fns.selection import exists_mol_res_spin_data, spin_loop
from relax_errors import RelaxDirError, RelaxFileError, RelaxFileOverwriteError, RelaxNoModelError, RelaxNoPdbError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNucleusError, RelaxProgFailError
from relax_io import mkdir_nofail, open_write_file, test_binary


def create(dir, force, binary, diff_search, sims, sim_type, trim, steps, constraints, heteronuc_type, atom1, atom2, spin_id):
    """Function for creating the Modelfree4 input files.

    The following files are created:
        dir/mfin
        dir/mfdata
        dir/mfpar
        dir/mfmodel
        dir/run.sh
    """

    # Test if the current pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if the PDB file is loaded (for the spheroid and ellipsoid).
    if hasattr(cdp, 'diff_tensor') and not cdp.diff_tensor.type == 'sphere' and not hasattr(cdp, 'structure'):
        raise RelaxNoPdbError

    # Directory creation.
    if dir == None:
        dir = pipe
    mkdir_nofail(dir, verbosity=0)

    # Number of field strengths and values.
    num_frq = 0
    frq = []
    for spin in spin_loop(spin_id):
        if hasattr(spin, 'num_frq'):
            if spin.num_frq > num_frq:
                # Number of field strengths.
                num_frq = spin.num_frq

                # Field strength values.
                for frq in spin.frq:
                    if frq not in frq:
                        frq.append(frq)

    # The 'mfin' file.
    mfin = open_write_file('mfin', dir, force)
    create_mfin(mfin)
    mfin.close()

    # Open the 'mfdata', 'mfmodel', and 'mfpar' files.
    mfdata = open_write_file('mfdata', dir, force)
    mfmodel = open_write_file('mfmodel', dir, force)
    mfpar = open_write_file('mfpar', dir, force)

    # Loop over the sequence.
    for spin in spin_loop(spin_id):
        if hasattr(spin, 'num_frq'):
            # The 'mfdata' file.
            if not create_mfdata(i, mfdata):
                continue

            # The 'mfmodel' file.
            create_mfmodel(i, mfmodel)

            # The 'mfpar' file.
            create_mfpar(i, mfpar)

    # Close the 'mfdata', 'mfmodel', and 'mfpar' files.
    mfdata.close()
    mfmodel.close()
    mfpar.close()

    # The 'run.sh' script.
    run = open_write_file('run.sh', dir, force)
    create_run(run)
    run.close()
    chmod(dir + '/run.sh', 0755)


def create_mfdata(i, file):
    """Create the Modelfree4 input file 'mfmodel'."""

    # Spin title.
    file.write("\nspin     " + spin.name + "_" + `spin.num` + "\n")

    # Data written flag.
    written = 0

    # Loop over the frequencies.
    for j in xrange(self.num_frq):
        # Set the data to None.
        r1, r2, noe = None, None, None

        # Loop over the relevant relaxation data.
        for k in xrange(spin.num_ri):
            if self.frq[j] != spin.frq[spin.remap_table[k]]:
                continue

            # Find the corresponding R1.
            if spin.ri_labels[k] == 'R1':
                r1 = spin.relax_data[k]
                r1_err = spin.relax_error[k]

            # Find the corresponding R2.
            elif spin.ri_labels[k] == 'R2':
                r2 = spin.relax_data[k]
                r2_err = spin.relax_error[k]

            # Find the corresponding NOE.
            elif spin.ri_labels[k] == 'NOE':
                noe = spin.relax_data[k]
                noe_err = spin.relax_error[k]

        # Test if the R1 exists for this frequency, otherwise skip the data.
        if r1:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('R1', self.frq[j]*1e-6, r1, r1_err, 1))
        else:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('R1', self.frq[j]*1e-6, 0, 0, 0))

        # Test if the R2 exists for this frequency, otherwise skip the data.
        if r2:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('R2', self.frq[j]*1e-6, r2, r2_err, 1))
        else:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('R2', self.frq[j]*1e-6, 0, 0, 0))

        # Test if the NOE exists for this frequency, otherwise skip the data.
        if noe:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('NOE', self.frq[j]*1e-6, noe, noe_err, 1))
        else:
            file.write('%-7s%-10.3f%20.15f%20.15f %-3i\n' % ('NOE', self.frq[j]*1e-6, 0, 0, 0))

        written = 1

    return written


def create_mfin(file):
    """Create the Modelfree4 input file 'mfin'."""

    # Set the diffusion tensor specific values.
    if cdp.diff_tensor.type == 'sphere':
        diff = 'isotropic'
        algorithm = 'brent'
        tm = cdp.diff.tm / 1e-9
        dratio = 1
        theta = 0
        phi = 0
    elif cdp.diff_tensor.type == 'spheroid':
        diff = 'axial'
        algorithm = 'powell'
        tm = cdp.diff.tm / 1e-9
        dratio = cdp.diff.Dratio
        theta = cdp.diff.theta * 360.0 / (2.0 * pi)
        phi = cdp.diff.phi * 360.0 / (2.0 * pi)
    elif cdp.diff_tensor.type == 'ellipsoid':
        diff = 'anisotropic'
        algorithm = 'powell'
        tm = cdp.diff.tm / 1e-9
        dratio = 0
        theta = 0
        phi = 0

    # Add the main options.
    file.write("optimization    tval\n\n")
    file.write("seed            0\n\n")
    file.write("search          grid\n\n")

    # Diffusion type.
    if cdp.diff.fixed:
        algorithm = 'fix'

    file.write("diffusion       " + diff + " " + self.diff_search + "\n\n")
    file.write("algorithm       " + algorithm + "\n\n")

    # Monte Carlo simulations.
    if self.sims:
        file.write("simulations     " + self.sim_type + "    " + `self.sims` + "       " + `self.trim` + "\n\n")
    else:
        file.write("simulations     none\n\n")

    selection = 'none'    # To be changed.
    file.write("selection       " + selection + "\n\n")
    file.write("sim_algorithm   " + algorithm + "\n\n")

    file.write("fields          " + `self.num_frq`)
    for frq in self.frq:
        file.write("  " + `frq*1e-6`)
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


def create_mfmodel(i, file):
    """Create the Modelfree4 input file 'mfmodel'."""

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Spin title.
    file.write("\nspin     " + spin.name + "_" + `spin.num` + "\n")

    # tloc.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'tloc', 0))
    if 'tm' in spin.params:
        file.write('%-4i' % 1)
    else:
        file.write('%-4i' % 0)

    if self.constraints:
        file.write('%-2i' % 2)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 20, self.steps))

    # Theta.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'Theta', 0))
    file.write('%-4i' % 0)

    if self.constraints:
        file.write('%-2i' % 2)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 90, self.steps))

    # S2f.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'Sf2', 1))
    if 'S2f' in spin.params:
        file.write('%-4i' % 1)
    else:
        file.write('%-4i' % 0)

    if self.constraints:
        file.write('%-2i' % 2)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 1, self.steps))

    # S2s.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'Ss2', 1))
    if 'S2s' in spin.params or 'S2' in spin.params:
        file.write('%-4i' % 1)
    else:
        file.write('%-4i' % 0)

    if self.constraints:
        file.write('%-2i' % 2)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 1, self.steps))

    # te.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'te', 0))
    if 'te' in spin.params or 'ts' in spin.params:
        file.write('%-4i' % 1)
    else:
        file.write('%-4i' % 0)

    if self.constraints:
        file.write('%-2i' % 2)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 10000, self.steps))

    # Rex.
    file.write('%-3s%-6s%-6.1f' % ('M1', 'Rex', 0))
    if 'Rex' in spin.params:
        file.write('%-4i' % 1)
    else:
        file.write('%-4i' % 0)

    if self.constraints:
        file.write('%-2i' % -1)
    else:
        file.write('%-2i' % 0)

    file.write('%11.3f%12.3f %-4s\n' % (0, 20, self.steps))


def create_mfpar(i, file):
    """Create the Modelfree4 input file 'mfpar'."""

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Spin title.
    file.write("\nspin     " + spin.name + "_" + `spin.num` + "\n")

    file.write('%-14s' % "constants")
    file.write('%-6i' % spin.num)
    file.write('%-7s' % spin.heteronuc_type)
    file.write('%-8.4f' % ([return_gyromagnetic_ratio(spin.heteronuc_type)] / 1e7))
    file.write('%-8.3f' % (spin.r * 1e10))
    file.write('%-8.3f\n' % (spin.csa * 1e6))

    file.write('%-10s' % "vector")
    file.write('%-4s' % self.atom1)
    file.write('%-4s\n' % self.atom2)


def create_run(file):
    """Create the script 'run.sh' for the execution of Modelfree4."""

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    file.write("#! /bin/sh\n")
    file.write(self.binary + " -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out")
    if cdp.diff_tensor.type != 'sphere':
        # Copy the pdb file to the model directory so there are no problems with the existance of *.rotate files.
        system('cp ' + cdp.structure.file_name + ' ' + self.dir)
        file.write(" -s " + cdp.structure.file_name.split('/')[-1])
    file.write("\n")


def execute(dir, force, binary):
    """Function for executing Modelfree4.

    BUG:  Control-C during execution causes the cwd to stay as dir.
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Arguments.
    self.pipe = pipe
    self.dir = dir
    self.force = force
    self.binary = binary

    # The current directory.
    orig_dir = getcwd()

    # The directory.
    if dir == None:
        dir = pipe
    if not access(dir, F_OK):
        raise RelaxDirError, ('Modelfree4', dir)

    # Change to this directory.
    chdir(dir)

    # Catch failures and return to the correct directory.
    try:
        # Test if the 'mfin' input file exists.
        if not access('mfin', F_OK):
            raise RelaxFileError, ('mfin input', 'mfin')

        # Test if the 'mfdata' input file exists.
        if not access('mfdata', F_OK):
            raise RelaxFileError, ('mfdata input', 'mfdata')

        # Test if the 'mfmodel' input file exists.
        if not access('mfmodel', F_OK):
            raise RelaxFileError, ('mfmodel input', 'mfmodel')

        # Test if the 'mfpar' input file exists.
        if not access('mfpar', F_OK):
            raise RelaxFileError, ('mfpar input', 'mfpar')

        # Test if the 'PDB' input file exists.
        if cdp.diff_tensor.type != 'sphere':
            pdb = cdp.structure.file_name.split('/')[-1]
            if not access(pdb, F_OK):
                raise RelaxFileError, ('PDB', pdb)
        else:
            pdb = None

        # Remove the file 'mfout' and '*.out' if the force flag is set.
        if force:
            for file in listdir(getcwd()):
                if search('out$', file) or search('rotate$', file):
                    remove(file)

        # Test the binary file string corresponds to a valid executable.
        test_binary(self.binary)

        # Execute Modelfree4 (inputting a PDB file).
        if pdb:
            status = spawnlp(P_WAIT, self.binary, self.binary, '-i', 'mfin', '-d', 'mfdata', '-p', 'mfpar', '-m', 'mfmodel', '-o', 'mfout', '-e', 'out', '-s', pdb)
            if status:
                raise RelaxProgFailError, 'Modelfree4'


        # Execute Modelfree4 (without a PDB file).
        else:
            status = spawnlp(P_WAIT, self.binary, self.binary, '-i', 'mfin', '-d', 'mfdata', '-p', 'mfpar', '-m', 'mfmodel', '-o', 'mfout', '-e', 'out')
            if status:
                raise RelaxProgFailError, 'Modelfree4'

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

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # The directory.
    if dir == None:
        dir = pipe
    if not access(dir, F_OK):
        raise RelaxDirError, ('Modelfree4', dir)

    # Test if the file exists.
    if not access(dir + "/mfout", F_OK):
        raise RelaxFileError, ('Modelfree4', dir + "/mfout")

    # Open the file.
    mfout_file = open(dir + "/mfout", 'r')
    mfout_lines = mfout_file.readlines()
    mfout_file.close()

    # Get the section line positions of the mfout file.
    s2_pos, s2f_pos, s2s_pos, te_pos, rex_pos, chi2_pos = line_positions(mfout_lines)

    # Find out if simulations were carried out.
    sims = 0
    for i in xrange(len(mfout_lines)):
        if search('_iterations', mfout_lines[i]):
            row = split(mfout_lines[i])
            sims = int(row[1])

    # Loop over the sequence.
    pos = 0
    for spin in spin_loop(spin_id):
        # Skip unselected residues.
        if not spin.select:
            continue

        # Test that the model has been set (needed to differentiate between te and ts).
        if not hasattr(spin, 'model'):
            raise RelaxNoModelError

        # Get the S2 data.
        if 'S2' in spin.params:
            spin.s2, spin.s2_err = get_mf_data(s2_pos + pos)

        # Get the S2f data.
        if 'S2f' in spin.params or 'S2s' in spin.params:
            spin.s2f, spin.s2f_err = get_mf_data(s2f_pos + pos)

        # Get the S2s data.
        if 'S2f' in spin.params or 'S2s' in spin.params:
            spin.s2s, spin.s2s_err = get_mf_data(s2s_pos + pos)

        # Get the te data.
        if 'te' in spin.params:
            spin.te, spin.te_err = get_mf_data(te_pos + pos)
            spin.te = spin.te / 1e12
            spin.te_err = spin.te_err / 1e12

        # Get the ts data.
        if 'ts' in spin.params:
            spin.ts, spin.ts_err = get_mf_data(te_pos + pos)
            spin.ts = spin.ts / 1e12
            spin.ts_err = spin.ts_err / 1e12

        # Get the Rex data.
        if 'Rex' in spin.params:
            spin.rex, spin.rex_err = get_mf_data(rex_pos + pos)
            spin.rex = spin.rex / (2.0 * pi * spin.frq[0])**2
            spin.rex_err = spin.rex_err / (2.0 * pi * spin.frq[0])**2

        # Get the chi-squared data.
        if not sims:
            row = split(mfout_lines[chi2_pos + pos])
            spin.chi2 = float(row[1])
        else:
            # The mfout chi2 position (with no sims) plus 2 (for the extra XML) plus the residue position times 22 (because of the simulated SSE rows).
            row = split(mfout_lines[chi2_pos + 2 + 22*pos])
            spin.chi2 = float(row[1])

        # Increment the residue position.
        pos = pos + 1


def get_mf_data(pos):
    """Extract the model-free data from the given position of the mfout file.

    This method is designed to catch a number of bugs in Modelfree4's mfout file.

    The first bug is the presence of a series of '*' characters causing a fusion of two columns.
    This is handled by splitting by the '*' char and then returning the first element.

    The second bug is when the floating point number is too big to fit into Modelfree4's string
    format limit of 15.3f.  This results in a results line such as:

    246      10000.00019682363392.000    1          0.000          0.000          0.000          0.000

    This is caught by scanning for two '.' characters in the column, and handled by assuming
    that every floating point number will have three decimal characters.

    @param pos:     The mfout line position.
    @type pos:      int
    @return:        The value and error.
    @rtype:         tuple of 2 floats
    """

    # Split the line up.
    row = split(self.mfout_lines[pos])

    # The value and error, assuming a bug free mfout file.
    val = row[1]
    err = row[4]

    # The Modelfree4 '*' column fusion bug.
    if search('\*', val) or search('\*', err):
        # Split by the '*' character.
        val_row = split(val, '*')
        err_row = split(err, '*')

        # The value and error (the first elements).
        val = val_row[0]
        err = err_row[0]

    # The Modelfree4 large float column fusion bug.
    new_row = []
    fused = False
    for element in row:
        # Count the number of '.' characters.
        num = count(element, '.')

        # Catch two or more '.' characters.
        if num > 1:
            # Set the fused flag.
            fused = True

            # Loop over each fused number.
            for i in xrange(num):
                # Find the index of the first '.'.
                index = find(element, '.')

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
        # Model-free data.
        if match('data_model_1', mfout_lines[i]):
            # Shift down two lines (to avoid the lines not starting with a space)..
            i = i + 2

            # Walk through all the data.
            while 1:
                # Break once the end of the data section is reached.
                if not mfout_lines[i] == '\n' and not search('^ ', mfout_lines[i]):
                    break

                # Split the line up.
                row = split(mfout_lines[i])

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
    return s2_pos, s2f_pos, s2s_pos, te_pos, rex_pos, chi2_pos
