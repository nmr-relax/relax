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
    def __init__(self, output_file='noe.out', seq_args=None, pipe_name='noe', noe_ref=None, noe_ref_rmsd=None, noe_sat=None, noe_sat_rmsd=None, unresolved=None, pdb_file=None, results_folder=None, int_method='height', heteronuc='N', proton='H', heteronuc_pdb='N'):
        """Perform relaxation curve fitting.

        @keyword output_file:   Name of the output file.
        @type output_file:      str
        @keyword seq_args:      The sequence data (file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep).  These are the arguments to the  sequence.read() user function, for more information please see the documentation for that function.
        @type seq_args:         list of lists of [str, None or str, None or int, None or int, None or int, None or int, None or int, None or int, None or int, None or str]
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
        @keyword unresolved:    Residues to exclude.
        @type unresolved:       str
        @keyword pdb_file:      Structure file in pdb format.
        @type pdb_file:         str
        @keyword results_folder:Folder where results files are placed in.
        @type results_folder:   str
        @keyword int_method:    The integration method, one of 'height', 'point sum' or 'other'.
        @type int_method:       str
        @keyword heteronuc:     Name of heteronucleus of peak list.
        @type heteronuc:        str
        @keyword proton:        Name of proton of peak list.
        @type proton:           str
        @keyword heteronuc_pdb: Name of heteronucleus of PDB file.
        @type heteronuc_pdb:    str
        """

        # Store the args.
        self.pipe_name = pipe_name
        self.output_file = output_file
        self.noe_sat = noe_sat
        self.noe_sat_rmsd = noe_sat_rmsd
        self.noe_ref = noe_ref
        self.noe_ref_rmsd =noe_ref_rmsd
        self.unresolved = unresolved
        self.pdb_file = pdb_file
        self.results_folder = results_folder
        if results_folder:
            self.grace_dir = results_folder+sep+'grace'
        else:
            self.grace_dir = None
        self.int_method = int_method
        self.heteronuc = heteronuc
        self.proton = proton
        self.heteronuc_pdb = heteronuc_pdb

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
        if self.pdb_file:   # load PDB File
            self.interpreter.structure.read_pdb(self.pdb_file)
            generic_fns.structure.main.load_spins(spin_id=heteronuc_pdb)

        else:
            self.interpreter.sequence.read(file=self.seq_args[0], dir=self.seq_args[1], mol_name_col=self.seq_args[2], res_num_col=self.seq_args[3], res_name_col=self.seq_args[4], spin_num_col=self.seq_args[5], spin_name_col=self.seq_args[6], sep=self.seq_args[7])

        # Load the reference spectrum and saturated spectrum peak intensities.
        self.interpreter.spectrum.read_intensities(file=self.noe_ref, spectrum_id='ref', int_method=self.int_method, heteronuc=self.heteronuc, proton=self.proton)
        self.interpreter.spectrum.read_intensities(file=self.noe_sat, spectrum_id='sat', int_method=self.int_method, heteronuc=self.heteronuc, proton=self.proton)

        # Set the spectrum types.
        self.interpreter.noe.spectrum_type('ref', 'ref')
        self.interpreter.noe.spectrum_type('sat', 'sat')

        # Set the errors.
        self.interpreter.spectrum.baseplane_rmsd(error=self.noe_ref_rmsd, spectrum_id='ref')
        self.interpreter.spectrum.baseplane_rmsd(error=self.noe_sat_rmsd, spectrum_id='sat')

        # Peak intensity error analysis.
        self.interpreter.spectrum.error_analysis()

        # Deselect unresolved spins.
        self.interpreter.deselect.read(file=self.unresolved)

        # Calculate the NOEs.
        self.interpreter.calc()

        # Save the NOEs.
        self.interpreter.value.write(param='noe', file=self.output_file, dir = self.results_folder, force=True)

        # Create grace files.
        self.interpreter.grace.write(y_data_type='ref', file='ref.agr', dir=self.grace_dir, force=True)
        self.interpreter.grace.write(y_data_type='sat', file='sat.agr', dir=self.grace_dir, force=True)
        self.interpreter.grace.write(y_data_type='noe', file='noe.agr', dir=self.grace_dir, force=True)

        # Write the results.
        self.interpreter.results.write(file='results', dir=self.results_folder, force=True)

        # Save the program state.
        self.interpreter.state.save(state = 'save', dir=self.results_folder, force=True)


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # Sequence data.


