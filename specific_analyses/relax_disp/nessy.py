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
"""Functions for interfacing with Michael Bieri's NESSY program."""

# Python module imports.
from os import getcwd

# relax module imports.
from lib.errors import RelaxError, RelaxNoSequenceError
from lib.io import mkdir_nofail, open_write_file
from lib.physical_constants import g1H, g15N
from pipe_control import pipes
from pipe_control.spectrometer import get_frequencies
from pipe_control.mol_res_spin import exists_mol_res_spin_data, spin_loop
from specific_analyses.relax_disp.disp_data import find_intensity_keys, loop_exp_frq, loop_exp_frq_point_time, loop_point, return_index_from_disp_point, return_index_from_frq


def nessy_input(file='save.NESSY', dir=None, spin_id=None, force=False):
    """Create the NESSY input files.

    @keyword dir:               The optional directory to place the files into.  If None, then the files will be placed into the current directory.
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
    if not hasattr(cdp, 'model_type'):
        raise RelaxError("The relaxation dispersion model has not been specified.")

    # Directory creation.
    if dir != None:
        mkdir_nofail(dir, verbosity=0)

    # The save file.
    save_file = open_write_file(file, dir, force)

    # Create the NESSY data object.
    data = Nessy_data(spin_id=spin_id)

    # Create the NESSY file.
    write_program_setup(file=save_file, dir=dir, data=data)

    # Loop over the experiments.
    for exp_index in range(data.num_exp):
        write_sequence(file=save_file, data=data, exp_index=exp_index)
        write_cpmg_datasets(file=save_file, data=data, exp_index=exp_index)
        write_spinlock_datasets(file=save_file, data=data, exp_index=exp_index)
        write_experiment_setup(file=save_file, data=data, exp_index=exp_index)


def write_cpmg_datasets(file=None, data=None, exp_index=0):
    """Create the NESSY CPMG datasets.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword data:      The NESSY data object.
    @type data:         Nessy_data instance
    @keyword exp_index: The index of the experiment to output.
    @type exp_index:    int
    """

    # Loop over the 30 elements.
    for i in range(30):
        # Empty data.
        file.write("Datasets:<>%s<>%i<>%s\n" % (exp_index, i+1, data.cpmg_data[exp_index][i]))


def write_experiment_setup(file=None, data=None, exp_index=0):
    """Create the NESSY experimental setup entries.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword data:      The NESSY data object.
    @type data:         Nessy_data instance
    @keyword exp_index: The index of the experiment to output.
    @type exp_index:    int
    """

    # The CPMG relaxation delay.
    file.write("CPMG relaxation delay:<>%s<>%s\n" % (exp_index, data.cpmg_delay[exp_index]))

    # The HD exchange entry
    file.write("HD Exchange:<>%s<>%s\n" % (exp_index, data.hd_exchange[exp_index]))

    # The experiment type.
    file.write("Experiment:<>%s<>%s\n" % (exp_index, data.experiment[exp_index]))

    # The nu_CPMG frequencies.
    file.write("CPMG frequencies:<>%s<>%s\n" % (exp_index, data.cpmg_frqs[exp_index]))

    # The spin-lock field strengths.
    file.write("Spin Lock / Offset:<>%s<>%s\n" % (exp_index, data.spin_lock[exp_index]))


def write_program_setup(file=None, dir=None, data=None):
    """Create the NESSY setup entries at the start of the file.

    @keyword file:  The file object to write to.
    @type file:     file object
    @keyword dir:   The optional directory to place the files into.  If None, then the files will be placed into the current directory.
    @type dir:      str or None
    @keyword data:  The NESSY data object.
    @type data:     Nessy_data instance
    """

    # File definition.
    file.write("NESSY save file<><>\n")

    # Program settings.
    file.write("Settings:<>['AICc', '500', '30', '2.0', '50.0', '0', '40']\n")
    file.write("Models:<>[1, 1, 1, 0, 0, 0, 0]\n")
    file.write("Fitting accuracy:<>1.49012e-20\n")

    # The project directory.
    if dir == None:
        dir = getcwd()
    file.write("Project folder:<>%s\n" % dir)

    # Experimental settings.
    file.write("CPMG delay:<>%s\n" % data.cpmg_delay)
    file.write("HD noise:<>%s\n" % data.hd_noise)
    file.write("Shift difference:<>%s\n" % data.shift_diff)
    file.write("Spec freq:<>%s\n" % data.spec_frq)
    file.write("B0:<>%s\n" % data.B0)
    file.write("PDB file:<>%s\n" % data.pdb_file)
    file.write("Number of experiments:<>%s\n" % data.num_exp)

    # Empty results files.
    file.write("Results:<>Plot<>[]\n")
    file.write("Results:<>Model1<>[]\n")
    file.write("Results:<>Model2<>[]\n")
    file.write("Results:<>Model3<>[]\n")
    file.write("Results:<>Model4<>[]\n")
    file.write("Results:<>Model5<>[]\n")
    file.write("Results:<>Model6<>[]\n")
    file.write("Results:<>Final<>[]\n")
    file.write("Results:<>ColorCode<>[]\n")
    file.write("Results:<>Textfiles:<>[]\n")
    file.write("Results:<>2D Plots:<>[]\n")
    file.write("Results:<>3D Plots:<>[]\n")
    file.write("Results:<>Intensities:<>[]\n")
    file.write("Final Results:<>[]\n")


def write_sequence(file=None, data=None, exp_index=0):
    """Create the NESSY sequence entry.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword data:      The NESSY data object.
    @type data:         Nessy_data instance
    @keyword exp_index: The index of the experiment to output.
    @type exp_index:    int
    """

    # Empty sequence.
    file.write("Sequence:<>%s<>%s\n" % (exp_index, data.sequence))


def write_spinlock_datasets(file=None, data=None, exp_index=0):
    """Create the NESSY R1rho datasets.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword data:      The NESSY data object.
    @type data:         Nessy_data instance
    @keyword exp_index: The index of the experiment to output.
    @type exp_index:    int
    """

    # Loop over the 30 elements.
    for i in range(30):
        # Loop over the second set of 30 elements.
        for j in range(30):
            # Empty data.
            file.write("Datasets Spinlock:<>%s<>%s<>%s<>%s\n" % (exp_index, i+1, j+1, data.r1rho_data[exp_index][i][j]))



class Nessy_data:
    def __init__(self, spin_id=None):
        """Create the NESSY data object container.

        @keyword spin_id:   The spin ID string to restrict data to.
        @type spin_id:      str
        """

        # Checks.
        if len(cdp.relax_time_list) != 1:
            raise RelaxError("NESSY only supports the fixed time relaxation dispersion experiments.")

        # The number of NESSY experiments (i.e. number of spectrometer frequencies).
        self.num_exp = 1
        if hasattr(cdp, 'spectrometer_frq_count'):
            self.num_exp = cdp.spectrometer_frq_count

        # Default values.
        self.cpmg_delay = ['0.04'] * self.num_exp
        self.hd_noise = ['1000'] * self.num_exp
        self.shift_diff = [None] * 700
        self.spec_frq = ['60.77'] * self.num_exp
        self.B0 = ['14.1'] * self.num_exp
        self.pdb_file = ''
        self.sequence = [''] * 700
        self.cpmg_data = []
        self.r1rho_data = []
        self.hd_exchange = []
        self.experiment = []
        self.cpmg_frqs = []
        self.spin_lock = []
        for exp_index in range(self.num_exp):
            self.cpmg_data.append([])
            self.r1rho_data.append([])
            self.hd_exchange.append([''] * 30)
            self.experiment.append('cpmg')
            self.cpmg_frqs.append([''] * 30)
            self.spin_lock.append([''] * 31)
            for i in range(30):
                self.cpmg_data[exp_index].append([''] * 700)
                self.r1rho_data[exp_index].append([])
                for j in range(30):
                    self.r1rho_data[exp_index][-1].append([''] * 700)

        # Assemble the data.
        self._assemble_experiment()
        self._assemble_cpmg_data(spin_id=spin_id)


    def _assemble_cpmg_data(self, spin_id=None):
        """Assemble the CPMG data.

        @keyword spin_id:   The spin ID string to restrict data to.
        @type spin_id:      str
        """

        # Spin loop.
        for spin, mol_name, res_num, res_name, id in spin_loop(full_info=True, selection=spin_id, return_id=True, skip_desel=True):
            # The residue index.
            res_index = res_num - 1

            # Sanity checks.
            if res_index < 0:
                raise RelaxError("A residue number of less than 1 is not supported in NESSY.")
            elif res_index > 699:
                raise RelaxError("A residue number of greater than 700 is not supported in NESSY.")

            # Loop over all spectrometer frequencies.
            for exp_type, frq in loop_exp_frq():
                # Loop over all dispersion points.
                field_index = 0
                for point in loop_point(exp_type=exp_type, skip_ref=False):
                    # Indices and keys.
                    exp_index = return_index_from_frq(frq)
                    point_index = return_index_from_disp_point(point, exp_type=exp_type)
                    keys = find_intensity_keys(exp_type=exp_type, frq=frq, point=point, time=cdp.relax_time_list[0])

                    # Convert the reference point for NESSY input.
                    if point == None:
                        point = 0

                    # Loop over the keys.
                    for key in keys:
                        # Another check.
                        if self.cpmg_data[exp_index][field_index][res_index] != '':
                            raise RelaxError("Only one spin system per residue is supported in NESSY.")

                        # Store the data (if it exists).
                        if key in spin.intensities:
                            self.cpmg_data[exp_index][field_index][res_index] = str(spin.intensities[key])

                        # The CPMG frequency.
                        self.cpmg_frqs[exp_index][field_index] = str(point)

                        # Increment the field index.
                        field_index += 1



    def _assemble_experiment(self):
        """Assemble the experimental data."""

        # Get the spectrometer info.
        frq_Hz = get_frequencies(units='MHz')
        frq_T = get_frequencies(units='T')

        # Loop over all data points.
        for exp_type, frq, point, time in loop_exp_frq_point_time():
            # The frequency index.
            frq_index = cdp.spectrometer_frq_list.index(frq)

            # The frequency data.
            self.cpmg_delay[frq_index] = str(time)

        # Loop over the experiments.
        for i in range(cdp.spectrometer_frq_count):
            # Spectrometer info.
            self.spec_frq[i] = str(frq_Hz[i] / g1H * g15N)
            self.B0[i] = str(frq_T[i])

