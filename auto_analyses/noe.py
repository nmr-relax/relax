###############################################################################
#                                                                             #
# Copyright (C) 2004-2011 Edward d'Auvergne                                   #
# Copyright (C) 2010 Michael Bieri                                            #
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

# Python module imports.
from os import sep

# relax module imports.
from generic_fns.pipes import cdp_name, has_pipe, switch
import generic_fns.structure.main
from prompt.interpreter import Interpreter
from status import Status; status = Status()



class NOE_calc:
    def __init__(self, pipe_name=None, file_root='noe', results_dir=None, save_state=True):
        """Perform relaxation curve fitting.

        To use this auto-analysis, a data pipe with all the required data needs to be set up.  This data pipe should contain the following:

            - All the spins loaded.
            - Unresolved spins deselected.
            - The NOE peak intensities from the saturated and reference spectra.
            - Either the baseplane noise RMDS values should be set or replicated spectra loaded.

        @keyword pipe_name:     The name of the data pipe containing all of the data for the analysis.
        @type pipe_name:        str
        @keyword file_root:     File root of the output filea.
        @type file_root:        str
        @keyword results_dir:   The directory where results files are saved.
        @type results_dir:      str
        @keyword save_state:    A flag which if True will cause a relax save state to be created at the end of the analysis.
        @type save_state:       bool
        """

        # Execution lock.
        status.exec_lock.acquire('auto noe')

        # Set up the analysis status object.
        status.init_auto_analysis(pipe_name, type='noe')

        # Store the args.
        self.save_state = save_state
        self.pipe_name = pipe_name
        self.file_root = file_root
        self.results_dir = results_dir
        if self.results_dir:
            self.grace_dir = results_dir + sep + 'grace'
        else:
            self.grace_dir = 'grace'

        # Data checks.
        self.check_vars()

        # Set the data pipe to the current data pipe.
        if self.pipe_name != cdp_name():
            switch(self.pipe_name)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Execute.
        self.run()

        # Finish and unlock execution.
        status.auto_analysis[self.pipe_name].fin = True
        status.exec_lock.release()


    def run(self):
        """Set up and run the NOE analysis."""

        # Peak intensity error analysis.
        self.interpreter.spectrum.error_analysis()

        # Calculate the NOEs.
        self.interpreter.calc()

        # Save the NOEs.
        self.interpreter.value.write(param='noe', file=self.file_root+'.out', dir=self.results_dir, force=True)

        # Save the results.
        self.interpreter.results.write(file='results', dir=self.results_dir, force=True)

        # Create Grace plots of the data.
        self.interpreter.grace.write(y_data_type='ref', file='ref.agr', dir=self.grace_dir, force=True)
        self.interpreter.grace.write(y_data_type='sat', file='sat.agr', dir=self.grace_dir, force=True)
        self.interpreter.grace.write(y_data_type='noe', file='noe.agr', dir=self.grace_dir, force=True)

        # Save the program state.
        if self.save_state:
            self.interpreter.state.save(state=self.file_root+'.save', dir=self.results_dir, force=True)


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # The pipe name.
        if not has_pipe(self.pipe_name):
            raise RelaxNoPipeError(self.pipe_name)
