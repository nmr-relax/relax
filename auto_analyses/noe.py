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

#python modules
import time
from os import sep

# relax module imports.
from prompt.interpreter import Interpreter
from generic_fns.pipes import cdp_name, has_pipe, switch
import generic_fns.structure.main
from status import Status; status = Status()



class NOE_calc:
    def __init__(self, pipe_name=None, output_file='noe.out', results_dir=None):
        """Perform relaxation curve fitting.

        To use this auto-analysis, a data pipe with all the required data needs to be set up.  This data pipe should contain the NOE peak intensities from the saturated and reference spectra, peak intensity errors either from the baseplane noise or replicated spectra, all of the spins loaded and unresolved spins deselected, 

        @keyword pipe_name:     The name of the data pipe containing all of the data for the analysis.
        @type pipe_name:        str
        @keyword output_file:   Name of the output file.
        @type output_file:      str
        @keyword results_dir:   Folder where results files are placed in.
        @type results_dir:      str
        @keyword int_method:    The integration method, one of 'height', 'point sum' or 'other'.
        @type int_method:       str
        """

        # Execution lock.
        status.exec_lock.acquire('auto noe')

        # Store the args.
        self.pipe_name = pipe_name
        self.output_file = output_file
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

        # Unlock execution.
        status.exec_lock.release()


    def run(self):
        """Set up and run the NOE analysis."""

        # Peak intensity error analysis.
        self.interpreter.spectrum.error_analysis()

        # Calculate the NOEs.
        self.interpreter.calc()

        # Save the NOEs.
        self.interpreter.value.write(param='noe', file=self.output_file, dir = self.results_dir, force=True)

        # Create grace files.
        self.interpreter.grace.write(y_data_type='ref', file='ref.agr', dir=self.grace_dir, force=True)
        self.interpreter.grace.write(y_data_type='sat', file='sat.agr', dir=self.grace_dir, force=True)
        self.interpreter.grace.write(y_data_type='noe', file='noe.agr', dir=self.grace_dir, force=True)

        # Write the results.
        self.interpreter.results.write(file='results', dir=self.results_dir, force=True)

        # Save the program state.
        self.interpreter.state.save(state = 'save', dir=self.results_dir, force=True)


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # The pipe name.
        if not has_pipe(self.pipe_name):
            raise RelaxNoPipeError(self.pipe_name)
