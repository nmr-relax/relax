###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""The automatic relaxation curve fitting protocol."""

# Python module imports.
from os import chmod, sep
from os.path import expanduser
from stat import S_IRWXU, S_IRGRP, S_IROTH
import sys

# relax module imports.
from lib.io import get_file_path, open_write_file
from lib.software.grace import script_grace2images
from lib.text.sectioning import section
from pipe_control.mol_res_spin import spin_loop
from pipe_control.pipes import cdp_name, has_pipe, switch
from prompt.interpreter import Interpreter
from status import Status; status = Status()


class Relax_fit:
    def __init__(self, pipe_name=None, pipe_bundle=None, file_root='rx', results_dir=None, grid_inc='11', mc_sim_num=500, view_plots=True):
        """Perform relaxation curve fitting.

        To use this auto-analysis, a data pipe with all the required data needs to be set up.  This data pipe should contain the following:

            - All the spins loaded.
            - Unresolved spins deselected.
            - All the peak intensities loaded and relaxation delay times set.
            - Either the baseplane noise RMDS values should be set or replicated spectra loaded.

        @keyword pipe_name:     The name of the data pipe containing all of the data for the analysis.
        @type pipe_name:        str
        @keyword pipe_bundle:   The data pipe bundle to associate all spawned data pipes with.
        @type pipe_bundle:      str
        @keyword file_root:     File root of the output filea.
        @type file_root:        str
        @keyword results_dir:   The directory where results files are saved.
        @type results_dir:      str
        @keyword grid_inc:      Number of grid search increments.
        @type grid_inc:         int
        @keyword mc_sim_num:    The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_sim_num:       int
        @keyword view_plots:    Flag to automatically view grace plots after calculation.
        @type view_plots:       bool
        """

        # Execution lock.
        status.exec_lock.acquire(pipe_bundle, mode='auto-analysis')

        # Set up the analysis status object.
        status.init_auto_analysis(pipe_bundle, type='relax_fit')
        status.current_analysis = pipe_bundle

        # Store the args.
        self.pipe_name = pipe_name
        self.pipe_bundle = pipe_bundle
        self.file_root = file_root
        self.results_dir = results_dir
        if self.results_dir:
            self.grace_dir = results_dir + sep + 'grace'
        else:
            self.grace_dir = 'grace'
        self.mc_sim_num = mc_sim_num
        self.grid_inc = grid_inc
        self.view_plots = view_plots

        # Data checks.
        self.check_vars()

        # Set the data pipe to the current data pipe.
        if self.pipe_name != cdp_name():
            switch(self.pipe_name)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Execute.
        self.run()

        # Finish and unlock execution.
        status.auto_analysis[self.pipe_bundle].fin = True
        status.current_analysis = None
        status.exec_lock.release()


    def run(self):
        """Set up and run the curve-fitting."""

        # Peak intensity error analysis.
        self.error_analysis()

        # Grid search.
        self.interpreter.minimise.grid_search(inc=self.grid_inc)

        # Minimise.
        self.interpreter.minimise.execute('newton', scaling=False, constraints=False)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
        self.interpreter.monte_carlo.create_data()
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise.execute('newton', scaling=False, constraints=False)
        self.interpreter.monte_carlo.error_analysis()

        # Save the relaxation rates.
        self.interpreter.value.write(param='rx', file=self.file_root+'.out', dir=self.results_dir, force=True)

        # Save the results.
        self.interpreter.results.write(file='results', dir=self.results_dir, force=True)

        # Determine the normalisation type.
        norm_type = 'last'
        for spin in spin_loop(skip_desel=True):
            if spin.model not in ['sat', 'inv']:
                norm_type = 'first'
                break

        # Create Grace plots of the data.
        self.interpreter.grace.write(y_data_type='chi2', file='chi2.agr', dir=self.grace_dir, force=True)    # Minimised chi-squared value.
        self.interpreter.grace.write(y_data_type='i0', file='i0.agr', dir=self.grace_dir, force=True)    # Initial peak intensity.
        self.interpreter.grace.write(y_data_type='rx', file=self.file_root+'.agr', dir=self.grace_dir, force=True)    # Relaxation rate.
        self.interpreter.grace.write(x_data_type='relax_times', y_data_type='peak_intensity', file='intensities.agr', dir=self.grace_dir, force=True)    # Average peak intensities.
        self.interpreter.grace.write(x_data_type='relax_times', y_data_type='peak_intensity', norm_type=norm_type, norm=True, file='intensities_norm.agr', dir=self.grace_dir, force=True)    # Average peak intensities (normalised).

        # Write a python "grace to PNG/EPS/SVG..." conversion script.
        # Open the file for writing.
        file_name = "grace2images.py"
        file_path = get_file_path(file_name=file_name, dir=self.grace_dir)
        file = open_write_file(file_name=file_name, dir=self.grace_dir, force=True)

        # Write the file.
        script_grace2images(file=file)

        # Close the batch script, then make it executable (expanding any ~ characters).
        file.close()

        if self.grace_dir:
            dir = expanduser(self.grace_dir)
            chmod(dir + sep + file_name, S_IRWXU|S_IRGRP|S_IROTH)
        else:
            file_name = expanduser(file_name)
            chmod(file_name, S_IRWXU|S_IRGRP|S_IROTH)


        # Display the Grace plots if selected.
        if self.view_plots:
            self.interpreter.grace.view(file='chi2.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file='i0.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file=self.file_root+'.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file='intensities.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file='intensities_norm.agr', dir=self.grace_dir)

        # Save the program state.
        self.interpreter.state.save(state=self.file_root+'.save', dir=self.results_dir, force=True)


    def error_analysis(self):
        """Perform an error analysis of the peak intensities."""

        # Printout.
        section(file=sys.stdout, text="Error analysis", prespace=2)

        # Check if intensity errors have already been calculated by the user.
        precalc = True
        for spin in spin_loop(skip_desel=True):
            # No structure.
            if not hasattr(spin, 'peak_intensity_err'):
                precalc = False
                break

            # Determine if a spectrum ID is missing from the list.
            for id in cdp.spectrum_ids:
                if id not in spin.peak_intensity_err:
                    precalc = False
                    break

        # Skip.
        if precalc:
            print("Skipping the error analysis as it has already been performed.")
            return

        # Check if there is replicates, and the user has not specified them.

        # Set flag for dublicates.
        has_dub = False

        if not hasattr(cdp, 'replicates'):
            # Collect all times, and matching spectrum ID.
            all_times = []
            all_id = []
            for spectrum_id in cdp.relax_times:
                all_times.append(cdp.relax_times[spectrum_id])
                all_id.append(spectrum_id)

            # Get the dublicates.
            dublicates = [(val, [i for i in range(len(all_times)) if all_times[i] == val]) for val in all_times]

            # Loop over the list of the mapping of times and duplications.
            list_dub_mapping = []
            for i, dub in enumerate(dublicates):
                # Get current spectum id.
                cur_spectrum_id = all_id[i]

                # Get the tuple of time and indexes of duplications.
                time, list_index_occur = dub

                # Collect mapping of index to id.
                id_list = []
                if len(list_index_occur) > 1:
                    # There exist dublications.
                    has_dub = True

                    for list_index in list_index_occur:
                        id_list.append(all_id[list_index])

                # Store to list
                list_dub_mapping.append((cur_spectrum_id, id_list))

        # If there is dublication, then assign them.
        if has_dub:
            # Assign dublicates.
            for spectrum_id, dub_pair in list_dub_mapping:
                if len(dub_pair) > 0:
                    self.interpreter.spectrum.replicated(spectrum_ids=dub_pair)

        # Run the error analysis.
        self.interpreter.spectrum.error_analysis()


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # The pipe name.
        if not has_pipe(self.pipe_name):
            raise RelaxNoPipeError(self.pipe_name)
