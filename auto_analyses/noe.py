###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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
import generic_fns.structure.main



class NOE_calc:
    def __init__(self, pipe_name='noe', noe_ref = None, noe_ref_rmsd = None, noe_sat = None, noe_sat_rmsd = None, freq = '', unresolved = None, pdb_file = None, results_folder = None, int_method='height', mc_num=500):
        """Perform relaxation curve fitting.

        @keyword pipe_name:     The name of the data pipe to create.
        @type pipe_name:        str
        @keyword noe_ref:       The NOE reference peak file.
        @type noe_ref:          file
        @keyword noe_ref_rmsd:  Background RMSD of reference NOE spectrum.
        @type noe_ref_rmsd:     int
        @keyword sat_ref:       The NOE saturated peak file.
        @type sat_ref:          file
        @keyword noe_sat_rmsd:  Background RMSD of saturated NOE spectrum.
        @type noe_sat_rmsd:     int
        @keyword frq:           Frequency of current set up.
        @type frq:              int
        @keyword unresolved:    Residues to exclude.
        @type unresolved:       str
        @keyword pdb_file:      Structure file in pdb format.
        @type pdb_file:         str
        @keyword results_folder:Folder where results files are placed in.
        @type results_folder:   str
        @keyword int_method:    The integration method, one of 'height', 'point sum' or 'other'.
        @type int_method:       str
        @keyword mc_num:        The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_num:           int
        """

        # Store the args.
        self.pipe_name = pipe_name + ' ' + str(time.asctime(time.localtime())) # add date and time to allow multiple executions of relax_fit
        self.noe_sat = noe_sat
        self.noe_sat_rmsd = noe_sat_rmsd
        self.noe_ref = noe_ref
        self.noe_ref_rmsd =noe_ref_rmsd
        self.frq = freq
        self.unresolved = unresolved
        self.pdb_file = pdb_file
        self.results_folder = results_folder
        self.grace_dir = results_folder + sep + 'grace'
        self.int_method = int_method
        self.mc_num = mc_num

        # User variable checks.
        self.check_vars()

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Execute.
        self.run()


    def run(self):
        """Set up and run the NOE analysis."""

        # Create the data pipe.
        self.interpreter.pipe.create(self.pipe_name, 'noe')

        # Load the sequence.
        if self.pdb_file == '!!! Sequence file selected !!!': # load sequence of file
            print 'Sequence file'  # FIXME
            #self.interpreter.sequence.read(file=self.seq_args[0], dir=self.seq_args[1], mol_name_col=self.seq_args[2], res_num_col=self.seq_args[3], res_name_col=self.seq_args[4], spin_num_col=self.seq_args[5], spin_name_col=self.seq_args[6], sep=self.seq_args[7])
            
        else:   # load PDB File
            self.interpreter.structure.read_pdb(self.pdb_file)
            generic_fns.structure.main.load_spins(spin_id='@N')
        
        # Update Progress bar
        print 'Progress: 20%'
        
        # Load the reference spectrum and saturated spectrum peak intensities.
        self.interpreter.spectrum.read_intensities(file=self.noe_ref, spectrum_id='ref', int_method=self.int_method, heteronuc='N', proton='H')
        self.interpreter.spectrum.read_intensities(file=self.noe_sat, spectrum_id='sat', int_method=self.int_method, heteronuc='N', proton='H')

        # Set the spectrum types.
        self.interpreter.noe.spectrum_type('ref', 'ref')
        self.interpreter.noe.spectrum_type('sat', 'sat')
        
        # Set the errors.
        self.interpreter.spectrum.baseplane_rmsd(error=self.noe_ref_rmsd, spectrum_id='ref')
        self.interpreter.spectrum.baseplane_rmsd(error=self.noe_sat_rmsd, spectrum_id='sat')
        
        # Update Progress bar
        print 'Progress: 40%'
        
        # Peak intensity error analysis.
        self.interpreter.spectrum.error_analysis()
        
        # Deselect unresolved spins.
        if self.unresolved == '':
            print ''
        else:
            self.interpreter.deselect.read(file='unresolved') # FIXME. relax should read the list without creating a file

        # Calculate the NOEs.
        self.interpreter.calc()

        # Update Progress bar
        print 'Progress: 60%'
        
        # Save the NOEs.
        self.interpreter.value.write(param='noe', file='noe_'+str(self.frq)+'.out', dir = self.results_folder, force=True)

        # Create grace files.
        self.interpreter.grace.write(y_data_type='ref', file='ref.agr', dir = self.grace_dir, force=True)
        self.interpreter.grace.write(y_data_type='sat', file='sat.agr', dir = self.grace_dir, force=True)
        self.interpreter.grace.write(y_data_type='noe', file='noe.agr', dir = self.grace_dir, force=True)

        # Update Progress bar
        print 'Progress: 80%'

        # Write the results.
        self.interpreter.results.write(file='results', dir=self.results_folder, force=True)

        # Save the program state.
        self.interpreter.state.save(state = 'save', dir=self.results_folder, force=True)

        # Update Progress bar
        print 'Progress: 100%'


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # Sequence data.


