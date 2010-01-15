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
        pipe.create(pipename, 'noe')
        
        # Load the backbone amide 15N spins from a PDB file.
        structure.read_pdb(str(struct_pdb))
        structure.load_spins(spin_id='@N')
        
        # Load the reference spectrum and saturated spectrum peak intensities.
        spectrum.read_intensities(file=str(noe_ref), spectrum_id='ref_ave')
        spectrum.read_intensities(file=str(noe_sat), spectrum_id='sat_ave')
        
        # Set the spectrum types.
        noe.spectrum_type('ref', 'ref_ave')
        noe.spectrum_type('sat', 'sat_ave')
        
        # Set the errors.
        spectrum.baseplane_rmsd(error=int(rmsd_ref), spectrum_id='ref_ave')
        spectrum.baseplane_rmsd(error=int(rmsd_sat), spectrum_id='sat_ave')
        
        # Peak intensity error analysis.
        spectrum.error_analysis()
        
        # Deselect unresolved residues.
        if not unres == '':
           print "\nDeselect residues" 
           selection.desel_read(file=resultsdir + sep + 'unresolved', res_num_col= 1)
        
        # Calculate the NOEs.
        calc()
        
        # Save the NOEs.
        value.write(param='noe', file=save_file, force=True)
        
        # Create grace files.
        grace.write(y_data_type='ref_ave', file='ref.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)
        grace.write(y_data_type='sat_ave', file='sat.' + str(nmr_freq) + '.agr', dir = gracedir,force=True)
        grace.write(y_data_type='noe', file='noe.' + str(nmr_freq) + '.agr', dir = gracedir,force=True)
        
        
        # Write the results.
        results.write(file='results', dir=resultsdir, force=True)
        
        # Save the program state.
        state.save('save', dir_name = resultsdir, force=True)
        
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
        success = True

        # Create PyMol Macro
        color_code_noe(self, target_dir)

        msgbox(msg='NOE calculation was successfull !', title='relaxGUI ', ok_button='OK', image=sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif', root=None)



