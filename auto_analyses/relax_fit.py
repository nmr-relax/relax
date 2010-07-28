###############################################################################
#                                                                             #
# Copyright (C) 2004-2010 Edward d'Auvergne                                   #
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
"""The automatic relaxation curve fitting protocol."""

#python modules
from os import sep

# relax module imports.
import generic_fns.structure.main
from prompt.interpreter import Interpreter



class Relax_fit:
    def __init__(self, file_root='rx', pipe_name='rx', results_directory=None, seq_args=None, file_names=None, relax_times=None, pdb_file=None, unresolved='unresolved', int_method='height', heteronuc='N', proton='H', load_spin_ids=None, mc_num=500, inc='11', view_plots=True):
        """Perform relaxation curve fitting.

        @keyword file_root:     File root of the output filea.
        @type file_root:        str
        @keyword pipe_name:     The name of the data pipe to create.
        @type pipe_name:        str
        @keyword results_directory:     The directory, where results files are saved.
        @type results_directory:        str
        @keyword seq_args:      The sequence data (file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep).  These are the arguments to the  sequence.read() user function, for more information please see the documentation for that function.
        @type seq_args:         list of lists of [str, None or str, None or int, None or int, None or int, None or int, None or int, None or int, None or int, None or str]
        @keyword file_names:    A list of all the peak list file names.
        @type file_names:       list of str
        @keyword relax_times:   The list of relaxation times corresponding to file_names.  These two lists must be of the same size.
        @type relax_times:      list of float
        @keyword pdb_file:      Name of the PDB file.
        @type pdb_file:         str
        @keyword unresolved:    Filename of the unresolved spin list.
        @type unresolved:       str
        @keyword int_method:    The integration method, one of 'height', 'point sum' or 'other'.
        @type int_method:       str
        @keyword heteronuc:     Label of hetero nucleus in the peak intensity file.
        @type heteronuc:        str
        @keyword proton:        Label of proton in the peak intensity file.
        @type proton:           str
        @keyword load_spin_ids: Id of spin to extract in PDB file.
        @type load_spin_ids:    str
        @keyword mc_num:        The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_num:           int
        @keyword inc:           Number of grid search increments.
        @type inc:              int
        @keyword view_plots:    Flag to automatically view grace plots after calculation.
        @type view_plots:       boolean
        """

        # Store the args.
        self.file_root = file_root
        self.pipe_name = pipe_name
        self.results_directory = results_directory
        if results_directory:
            self.grace_dir = results_directory+sep+'grace'
        else:
            self.grace_dir = None
        self.seq_args = seq_args
        self.file_names = file_names
        self.relax_times = relax_times
        self.pdb_file = pdb_file
        self.unresolved = unresolved
        self.view_plots = view_plots
        self.int_method = int_method
        self.heteronuc = heteronuc
        self.proton = proton
        self.load_spin_ids = load_spin_ids
        self.mc_num = mc_num
        self.inc = inc

        # User variable checks.
        self.check_vars()

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Execute.
        self.run()


    def run(self):
        """Set up and run the curve-fitting."""

        # Create the data pipe.
        self.interpreter.pipe.create(self.pipe_name, 'relax_fit')

        # Load the sequence.
        if self.pdb_file:   # load PDB File
            self.interpreter.structure.read_pdb(self.pdb_file)
            generic_fns.structure.main.load_spins(spin_id=self.load_spin_ids)

        else:
            self.interpreter.sequence.read(file=self.seq_args[0], dir=self.seq_args[1], mol_name_col=self.seq_args[2], res_num_col=self.seq_args[3], res_name_col=self.seq_args[4], spin_num_col=self.seq_args[5], spin_name_col=self.seq_args[6], sep=self.seq_args[7])

        # Loop over the spectra.
        for i in xrange(len(self.file_names)):
            # Load the peak intensities.
            self.interpreter.spectrum.read_intensities(file=self.file_names[i], spectrum_id=self.file_names[i], int_method=self.int_method, heteronuc=self.heteronuc, proton=self.proton)

            # Set the relaxation times.
            self.interpreter.relax_fit.relax_time(time=self.relax_times[i], spectrum_id=self.file_names[i])

        # Specify the duplicated spectra.
        for i in range(len(self.file_names)):
            for j in range(i+1, len(self.file_names)):
                # Relax times match, so this is a replicate.
                if self.relax_times[i] == self.relax_times[j]:
                    self.interpreter.spectrum.replicated(spectrum_ids=[self.file_names[i], self.file_names[j]])

        # Peak intensity error analysis.
        self.interpreter.spectrum.error_analysis()

        # Deselect unresolved spins.
        self.interpreter.deselect.read(file=self.unresolved)

        # Set the relaxation curve type.
        self.interpreter.relax_fit.select_model('exp')

        # Grid search.
        self.interpreter.grid_search(inc=self.inc)

        # Minimise.
        self.interpreter.minimise('simplex', scaling=False, constraints=False)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=self.mc_num)
        self.interpreter.monte_carlo.create_data()
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise('simplex', scaling=False, constraints=False)
        self.interpreter.monte_carlo.error_analysis()

        # Save the relaxation rates.
        self.interpreter.value.write(param='rx', file=self.file_root+'.out', dir=self.results_directory, force=True)

        # Save the results.
        self.interpreter.results.write(file='results', dir=self.results_directory, force=True)

        # Create Grace plots of the data.
        self.interpreter.grace.write(y_data_type='chi2', file='chi2.agr', dir=self.grace_dir, force=True)    # Minimised chi-squared value.
        self.interpreter.grace.write(y_data_type='i0', file='i0.agr', dir=self.grace_dir, force=True)    # Initial peak intensity.
        self.interpreter.grace.write(y_data_type='rx', file=self.file_root+'.agr', dir=self.grace_dir, force=True)    # Relaxation rate.
        self.interpreter.grace.write(x_data_type='relax_times', y_data_type='int', file='intensities.agr', dir=self.grace_dir, force=True)    # Average peak intensities.
        self.interpreter.grace.write(x_data_type='relax_times', y_data_type='int', norm=True, file='intensities_norm.agr', dir=self.grace_dir, force=True)    # Average peak intensities (normalised).

        # Display the Grace plots if selected.
        if self.view_plots:
            self.interpreter.grace.view(file='chi2.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file='i0.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file=self.file_root+'.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file='intensities.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file='intensities_norm.agr', dir=self.grace_dir)

        # Save the program state.
        self.interpreter.state.save(self.file_root+'.save', dir=self.results_directory, force=True)


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # Sequence data.
        if not isinstance(self.seq_args, list):
            raise RelaxError("The seq_args user variable '%s' must be a list." % self.seq_args)
        if len(self.seq_args) != 8:
            raise RelaxError("The seq_args user variable '%s' must be a list with eight elements." % self.seq_args)
        if not isinstance(self.seq_args[0], str):
            raise RelaxError("The file name component of the seq_args user variable '%s' must be a string." % self.seq_args)
        for i in range(1, 8):
            if self.seq_args[i] != None and not isinstance(self.seq_args[i], int):
                raise RelaxError("The column components of the seq_args user variable '%s' must be either None or integers." % self.seq_args)


