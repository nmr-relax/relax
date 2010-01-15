###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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

# Python module imports.
from os import getcwd, listdir, sep
from string import replace
import time
import sys
import os

# relax module imports.
from float import floatAsByteArray
from generic_fns.mol_res_spin import generate_spin_id, spin_index_loop, spin_loop
from generic_fns import pipes
import generic_fns.structure.main
from relax_errors import RelaxError
from specific_fns.setup import noe_obj
from generic_fns.state import save_state

# relaxGUI module import
from results_analysis import color_code_noe
from message import relax_run_ok


#NOE calculation

def make_noe(target_dir, noe_ref, noe_sat, rmsd_ref, rmsd_sat, nmr_freq, struct_pdb, unres, execute, self, freqno, global_setting, file_setting, sequencefile):
        hetero = global_setting[2]
        prot = global_setting[3]
        intcol = int(file_setting[5])
        mol_name = int(file_setting[0])
        res_num = int(file_setting[1])
        res_name = int(file_setting[2])
        spin_num = int(file_setting[3])
        spin_name = int(file_setting[4])
        resultsdir = str(target_dir)
        gracedir = str(target_dir) + sep + 'grace'
        save_file = str(target_dir) + sep + 'noe.' + str(nmr_freq)  + '.out'
        noe_ref_1 = noe_ref
        noe_sat_1 = noe_sat
        unres = str(unres)

        #create unresolved file
        if not unres == '':
           print "\nCreate unresolved file"
           unres = replace(unres, ",","\n")
           unres = replace(unres, " ","")
           filename3 = target_dir + sep + 'unresolved'
           unresolved = open(filename3, 'w')
           unresolved.write(unres)
           unresolved.close()


        pipename = 'NOE ' + str(time.asctime(time.localtime()))

        # Create the NOE data pipe.
        print "pipe.create("+pipename+")"
        pipes.create(pipename, 'noe')

        # Load Sequence
        if str(struct_pdb) == '!!! Sequence file selected !!!':
            
             # Read sequence file
             print "\nLoad sequence from "+ sequencefile
             sequence.read(sequencefile, res_name_col = 1)
        
        else:
             # Load the backbone amide 15N spins from a PDB file.
             print "\nLoad sequence from "+ str(struct_pdb)
             generic_fns.structure.main.read_pdb(str(struct_pdb))
             generic_fns.structure.main.load_spins(spin_id='@N')
        
        # Load the reference spectrum and saturated spectrum peak intensities.
        print "\nspectrum.read(file="+str(noe_ref)+", spectrum_id='ref_spec', heteronuc="+hetero+", proton="+prot+", int_method='height')"
        spectrum.read(file=str(noe_ref), spectrum_id='ref_spec', heteronuc=hetero, proton=prot, int_method='height')
        print "\nspectrum.read(file="+str(noe_sat)+", spectrum_id='sat_spec', heteronuc="+hetero+", proton="+prot+", int_method='height')"
        spectrum.read(file=str(noe_sat), spectrum_id='sat_spec', heteronuc=hetero, proton=prot, int_method='height')
        
        # Set the spectrum types.
        noe_obj._spectrum_type('ref', 'ref_spec')
        noe_obj._spectrum_type('sat', 'sat_spec')
        
        # Set the errors.
        spectrum.baseplane_rmsd(error=int(rmsd_ref), spectrum_id='ref_spec')
        spectrum.baseplane_rmsd(error=int(rmsd_sat), spectrum_id='sat_spec')
        
        # Peak intensity error analysis.
        print "\nspectrum.error_analysis()"
        spectrum.error_analysis()
        
        # Deselect unresolved residues.
        if not unres == '':
           print "\nDeselect residues" 
           selection.desel_read(file=resultsdir + sep + 'unresolved', res_num_col= 1)
        
        # Calculate the NOEs.
        print "\nminimise.calc()"
        minimise.calc()
        
        # Save the NOEs.
        print "\nSave Files:\n"
        value.write(param='noe', file=save_file, force=True)
        
        # Create grace files.
        grace.write(y_data_type='ref_spec', file='ref.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)
        grace.write(y_data_type='sat_spec', file='sat.' + str(nmr_freq) + '.agr', dir = gracedir,force=True)
        grace.write(y_data_type='noe', file='noe.' + str(nmr_freq) + '.agr', dir = gracedir,force=True)
        
        
        # Write the results.
        results.write(file='results', directory=resultsdir, force=True)
        
        # Save the program state.
        save_state('save', dir = resultsdir, force=True)
        
        print ""
        print ""
        print ""
        print "____________________________________________________________________________"
        print ""
        print "calculation finished"
        print ""
        if freqno == 1:
                     self.m_noe_1.SetValue(target_dir + sep + 'noe.' + str(nmr_freq) + '.out')
        if freqno == 2:
                     self.m_noe_2.SetValue(target_dir + sep + 'noe.' + str(nmr_freq) + '.out')
        if freqno == 3:
                     self.m_noe_3.SetValue(target_dir + sep + 'noe.' + str(nmr_freq) + '.out')
        self.list_noe.Append(target_dir + sep + 'grace' + sep + 'noe.' + str(nmr_freq) + '.agr')

        # Create PyMol Macro
        color_code_noe(self, target_dir)

        relax_run_ok('NOE calculation was successful !')
