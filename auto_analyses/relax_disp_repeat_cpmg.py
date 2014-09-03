###############################################################################
#                                                                             #
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
"""The automatic relaxation dispersion protocol for repeated data for CPMG.

U{task #7826<https://gna.org/task/index.php?78266>}, Write an python class for the repeated analysis of dispersion data.
"""

# Python module imports.
from datetime import datetime
from glob import glob
from os import getcwd, sep

# relax module imports.
from lib.io import sort_filenames
from prompt.interpreter import Interpreter
from specific_analyses.relax_disp.variables import MODEL_R2EFF
from status import Status; status = Status()


# Define sfrq key to dic.
DIC_KEY_FORMAT = "%.8f"


class Relax_disp_rep:

    """The relaxation dispersion analysis for repeated data."""

    # Some class variables.
    opt_func_tol = 1e-25
    opt_max_iterations = int(1e7)

    def __init__(self, settings):
        """Perform a repeated dispersion analysis for settings given."""

        # Unpack settings from dictionary to self.
        for setting, value in settings.iteritems():
            setattr(self, setting, value)

        # Standard settings.
        if not hasattr(self, 'pipe_name'):
            setattr(self, 'pipe_name', 'base_pipe')

        if not hasattr(self, 'pipe_bundle'):
            setattr(self, 'pipe_bundle', 'repeat')

        if not hasattr(self, 'time'):
            setattr(self, 'time', datetime.now().strftime('%Y_%m_%d_%H_%M'))

        # No results directory, so default to the current directory.
        if not hasattr(self, 'results_dir'):
            setattr(self, 'results_dir', getcwd() + sep + 'results' + sep + self.time )

        # If no models, then just R2eff
        if not hasattr(self, 'models'):
            setattr(self, 'models', [MODEL_R2EFF] )

        # Standard Grid Search.
        if not hasattr(self, 'grid_inc'):
            setattr(self, 'grid_inc', 11 )

        # Standard Monte-Carlo simulations.
        if not hasattr(self, 'mc_sim_num'):
            setattr(self, 'mc_sim_num', 40 )

        # Standard Monte-Carlo simulations for exponential fit. '-1' is getting R2eff err from Co-variance.
        if not hasattr(self, 'exp_mc_sim_num'):
            setattr(self, 'exp_mc_sim_num', -1 )

        # Standard model selection.
        if not hasattr(self, 'modsel'):
            setattr(self, 'modsel', 'AIC' )

        # The R2eff/R1rho value in rad/s by which to judge insignificance.  If the maximum difference between two points on all dispersion curves for a spin is less than this value, that spin will be deselected.  
        # This does not affect the 'No Rex' model.  Set this value to 0.0 to use all data.  The value will be passed on to the relax_disp.insignificance user function.
        if not hasattr(self, 'insignificance'):
            setattr(self, 'insignificance', 1.0 )

        # A flag which if True will set the grid R20 values from the minimum R2eff values through the r20_from_min_r2eff user function. 
        # This will speed up the grid search with a factor GRID_INC^(Nr_spec_freq). For a CPMG experiment with two fields and standard GRID_INC=21, the speed-up is a factor 441.
        if not hasattr(self, 'set_grid_r20'):
            setattr(self, 'set_grid_r20', True )

        # Define glop pattern for ser files.
        glob_pat = '*.ser'

        # Loop over peak files.
        for sfrq in self.sfrqs:
            # Access the key in self.
            key = DIC_KEY_FORMAT % (sfrq)
            peaks_folder = getattr(self, key)['peaks_folder']

            # Get the file list.
            file_list = glob(peaks_folder + sep + glob_pat)

            # Sort the file list Alphanumeric, reverted.
            file_list_sort = sort_filenames(filenames=file_list, rev=True)

            for cur_file in file_list_sort:
                print(key, cur_file)

        # Define glop pattern for ser files.
        glob_pat = '*.rmsd'

        # Loop over rmsd files.
        for sfrq in self.sfrqs:
            # Access the key in self.
            key = DIC_KEY_FORMAT % (sfrq)
            rmsd_folder = getattr(self, key)['rmsd_folder']

            # Get the file list.
            file_list = glob(rmsd_folder + sep + glob_pat)

            # Sort the file list Alphanumeric, reverted.
            file_list_sort = sort_filenames(filenames=file_list, rev=True)

            for cur_file in file_list_sort:
                print(key, cur_file)


        # Load the interpreter.
        #self.interpreter = Interpreter(show_script=False, raise_relax_error=True)
        #self.interpreter.populate_self()
        #self.interpreter.on(verbose=False)



