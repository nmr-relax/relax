###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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
"""Functions for interfacing with Flemming Hansen's CATIA program."""

# Dependencies.
import dep_check

# Python module imports.
from os import F_OK, access, chdir, getcwd, sep
PIPE, Popen = None, None
if dep_check.subprocess_module:
    from subprocess import PIPE, Popen
import sys

# relax module imports.
from lib.dispersion.variables import EXP_TYPE_CPMG_SQ
from lib.errors import RelaxError, RelaxDirError
from lib.io import mkdir_nofail, open_write_file, test_binary
from pipe_control.mol_res_spin import check_mol_res_spin_data, spin_loop
from pipe_control.pipes import check_pipe
from specific_analyses.relax_disp.checks import check_model_type, check_spectra_id_setup
from specific_analyses.relax_disp.data import loop_frq, loop_offset_point, return_param_key_from_data


def catia_execute(file='Fit.catia', dir=None, binary=None):
    """Create the CATIA input files.

    @keyword file:          The main CATIA execution file.
    @type file:             str
    @keyword dir:           The optional directory to place the files into.  If None, then the files will be placed into the current directory.
    @type dir:              str or None
    @keyword binary:        The name of the CATIA binary file.  This can include the path to the binary.
    @type binary:           str
    """

    # The current directory.
    orig_dir = getcwd()

    # Test the binary file string corresponds to a valid executable.
    test_binary(binary)

    # The directory.
    if dir == None:
        dir = orig_dir
    if not access(dir, F_OK):
        raise RelaxDirError('CATIA', dir)

    # Change to the directory with the CATIA input files.
    chdir(dir)

    # Catch failures and return to the correct directory.
    try:
        # Execute CATIA.
        cmd = binary + ' < Fit.catia'
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

    # Failure.
    except:
        # Change back to the original directory.
        chdir(orig_dir)

        # Reraise the error.
        raise

    # Change back to the original directory.
    chdir(orig_dir)


def catia_input(file='Fit.catia', dir=None, output_dir='output', force=False):
    """Create the CATIA input files.

    @keyword file:          The main CATIA execution file.
    @type file:             str
    @keyword dir:           The optional directory to place the files into.  If None, then the files will be placed into the current directory.
    @type dir:              str or None
    @keyword output_dir:    The CATIA output directory, located within the directory specified by the dir argument.  This directory will be created.
    @type output_dir:       str
    @keyword force:         A flag which if True will cause all pre-existing files to be overwritten.
    @type force:            Bool
    """

    # Data checks.
    check_pipe()
    check_mol_res_spin_data()
    check_spectra_id_setup()
    check_model_type()

    # Check that this is CPMG data.
    for id in cdp.spectrum_ids:
        if cdp.exp_type[id] != 'SQ CPMG':
            raise RelaxError("Only CPMG type data is supported.")

    # Directory creation.
    if dir != None:
        mkdir_nofail(dir, verbosity=0)

    # Create the R2eff files.
    write_r2eff_files(input_dir='input_r2eff', base_dir=dir, force=force)

    # Create the parameter files.
    write_param_files(global_file="ParamGlobal.inp", set_file="ParamSet1.inp", dir=dir, force=force)

    # Create the main execution file.
    write_main_file(file=file, dir=dir, output_dir=output_dir, force=force)

    # Create the output directory as needed by CATIA (it does not create it itself).
    mkdir_nofail(dir + sep + output_dir, verbosity=0)


def write_main_file(file=None, dir=None, output_dir=None, f_tol=1e-25, max_iter=10000000, r1=False, force=False):
    """Create the main CATIA execution file.

    @keyword file:          The main CATIA execution file.
    @type file:             str
    @keyword dir:           The directory to place the files into.
    @type dir:              str or None
    @keyword output_dir:    The CATIA output directory, located within the directory specified by the dir argument.  This directory will be created.
    @type output_dir:       str
    @keyword r1:            A flag which if True will cause the R1 data to be used for off-resonance effects.
    @type r1:               bool
    @keyword force:         A flag which if True will cause a pre-existing file to be overwritten.
    @type force:            bool
    """

    # The file.
    catia_in = open_write_file(file_name=file, dir=dir, force=force)

    # The R2eff input sets.
    for frq in loop_frq():
        frq_label = int(frq*1e-6)
        file_name = "data_set_%i.inp" % frq_label
        catia_in.write("ReadDataset(%s)\n" % file_name)

    # Write out the data.
    catia_in.write("ReadParam_Global(ParamGlobal.inp)\n")
    catia_in.write("ReadParam_Local(ParamSet1.inp)\n")
    catia_in.write("\n")

    # The R1 data for off-resonance effects.
    if r1:
        catia_in.write("ReadParam(Omega;%s;0;1)\n" % shift_file)
        for frq in loop_frq():
            frq_label = int(frq*1e-6)
            param = "R1iph_%s" % frq_label
            r1_file = "R1_%s.out" % frq_label
            catia_in.write("ReadParam(%s;%s;0;1)\n" % (param, r1_file))
        catia_in.write("\n")

    # Fix these off-resonance parameters.
    catia_in.write("FreeLocalParam(all;Omega;false)\n")
    for frq in loop_frq():
        frq_label = int(frq*1e-6)
        param = "R1iph_%s" % frq_label
        catia_in.write("FreeLocalParam(all;%s;false)\n" % param)
    catia_in.write("\n")

    # Minimisation.
    catia_in.write("Minimize(print=y;tol=%s;maxiter=%i)\n" % (f_tol, max_iter))
    catia_in.write("\n")

    # Plotting.
    catia_in.write("PrintParam(%s/GlobalParam.fit;global)\n" % output_dir)
    catia_in.write("PrintParam(%s/DeltaOmega.fit;DeltaO)\n" % output_dir)
    catia_in.write("PrintData(%s/)\n" % output_dir)
    catia_in.write("\n")

    # Calculate the chi-squared value (not sure why, it's calculated in the minimisation).
    catia_in.write("ChiSq(all;all)\n")

    # Exit the program.
    catia_in.write("exit(0)\n")

    # Close the file.
    catia_in.close()


def write_param_files(global_file=None, kex=1500.0, pA=0.95, set_file=None, dir=None, r1=False, force=False):
    """Create the CATIA parameter files.

    @keyword global_file:   The name of the global parameter file.
    @type global_file:      str
    @keyword set_file:      The name of the parameter set file.
    @type set_file:         str
    @keyword dir:           The base directory to place the files into.
    @type dir:              str
    @keyword r1:            A flag which if True will cause the R1 data to be used for off-resonance effects.
    @type r1:               bool
    @keyword force:         A flag which if True will cause a pre-existing file to be overwritten.
    @type force:            bool
    """

    # Open the global parameter file.
    param_file = open_write_file(file_name=global_file, dir=dir, force=force)

    # Set the starting values.
    param_file.write("kex = %s\n" % kex)
    param_file.write("pb = %s\n" % (1.0-pA))

    # Close the file.
    param_file.close()

    # Open the 1st parameter set file.
    set_file = open_write_file(file_name=set_file, dir=dir, force=force)

    # The parameter format.
    params = ['Delta0']
    values = [0.5]
    if r1:
        for frq in loop_frq():
            params.append("R1iph_%s" % frq_label(frq))
            values.append(1.5)
    for frq in loop_frq():
        params.append("R0iph_%s" % frq_label(frq))
        values.append(5.0)
    if r1:
        params.append("Omega")
        values.append(0.0)

    # Write out the format.
    set_file.write("format = (")
    for i in range(len(params)):
        if i != 0:
            set_file.write(';')
        set_file.write(params[i])
    set_file.write(")\n")

    # Um?!?  The average values maybe?
    set_file.write("* = (")
    for i in range(len(values)):
        if i != 0:
            set_file.write(';')
        set_file.write("%s" % values[i])
    set_file.write(")\n")

    # Close the file.
    set_file.close()


def frq_label(frq):
    """Convert the frequency in Hz to a label in MHz.

    @param frq: The frequency to convert.
    @type frq:  float
    @return:    The frequency in MHz as a label.
    @rtype:     str
    """

    # Convert and return.
    return str(int(frq*1e-6))


def write_r2eff_files(input_dir=None, base_dir=None, force=False):
    """Create the CATIA R2eff input files.

    @keyword input_dir: The special directory for the R2eff input files.
    @type input_dir:    str
    @keyword base_dir:  The base directory to place the files into.
    @type base_dir:     str
    @keyword force:     A flag which if True will cause a pre-existing file to be overwritten.
    @type force:        bool
    """

    # Create the directory for the R2eff files for each field and spin.
    dir = base_dir + sep + input_dir
    mkdir_nofail(dir, verbosity=0)

    # Determine the isotope information.
    isotope = None
    for spin in spin_loop(skip_desel=True):
        if hasattr(spin, 'isotope'):
            if isotope == None:
                isotope = spin.isotope
            elif spin.isotope != isotope:
                raise RelaxError("CATIA only supports one spin type.")
    if isotope == None:
        raise RelaxError("The spin isotopes have not been specified.")

    # Isotope translation.
    if isotope == '1H':
        isotope = 'H1'
    elif isotope == '13C':
        isotope = 'C13'
    elif isotope == '15N':
        isotope = 'N15'

    # Loop over the frequencies.
    for frq, mi in loop_frq(return_indices=True):
        # The frequency string in MHz.
        frq_string = int(frq*1e-6)

        # The set files.
        file_name = "data_set_%i.inp" % frq_string
        set_file = open_write_file(file_name=file_name, dir=base_dir, force=force)
        id = frq_string
        set_file.write("ID=%s\n" % id)
        set_file.write("Sfrq = %s\n" % frq_string)
        set_file.write("Temperature = %s\n" % 0.0)
        set_file.write("Nucleus = %s\n" % isotope)
        set_file.write("Couplednucleus = %s\n" % 'H1')
        set_file.write("Time_equil = %s\n" % 0.0)
        set_file.write("Pwx_cp = %s\n" % 0.0)
        set_file.write("Taub = %s\n" % 0.0)
        set_file.write("Time_T2 = %s\n"% cdp.relax_time_list[0])
        set_file.write("Xcar = %s\n" % 0.0)
        set_file.write("Seqfil = %s\n" % 'CW_CPMG')
        set_file.write("Minerror = %s\n" % "(2.%;0.5/s)")
        set_file.write("Basis = (%s)\n" % "Iph_7")
        set_file.write("Format = (%i;%i;%i)\n" % (0, 1, 2))
        set_file.write("DataDirectory = %s\n" % (dir+sep))
        set_file.write("Data = (\n")

        # Loop over the spins.
        for spin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            # The file.
            file_name = "spin%s_%i.cpmg" % (spin_id.replace('#', '_').replace(':', '_').replace('@', '_'), frq_string)
            spin_file = open_write_file(file_name=file_name, dir=dir, force=force)

            # Write the header.
            spin_file.write("# %18s %20s %20s\n" % ("nu_cpmg(Hz)", "R2(1/s)", "Esd(R2)"))

            # Loop over the dispersion points.
            for offset, point, oi, di in loop_offset_point(exp_type=EXP_TYPE_CPMG_SQ, frq=frq, return_indices=True):
                # The key.
                key = return_param_key_from_data(exp_type=EXP_TYPE_CPMG_SQ, frq=frq, offset=offset, point=point)

                # No data.
                if key not in spin.r2eff:
                    continue

                # Write out the data.
                spin_file.write("%20.15f %20.15f %20.15f\n" % (point, spin.r2eff[key], spin.r2eff_err[key]))

            # Close the file.
            spin_file.close()

            # Add the file name to the set.
            catia_spin_id = "%i%s" % (res_num, spin.name)
            set_file.write(" [%s;%s];\n" % (catia_spin_id, file_name))

        # Terminate the set file.
        set_file.write(")\n")
        set_file.close()
