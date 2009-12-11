###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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

# script to calculate rx

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
from specific_fns.setup import relax_fit_obj
from generic_fns.state import save_state
from generic_fns import monte_carlo
from minfx.generic import generic_minimise


def make_tx(target_dir, relax_times, structure_pdb, nmr_freq, t1_t2, freq_no, unres, self, freqno):

        success = False
        resultsdir = str(target_dir)
        gracedir = str(target_dir) + '/grace'
        savefile = str(target_dir) + '/r' + str(t1_t2) + '.' + str(nmr_freq)  + '.out'


        # Select Peak Lists and Relaxation Times 
        if t1_t2 == 1:
            if freq_no == 1:
              peakfiles = t1_list
            if freq_no == 2:
              peakfiles = t1_list2
            if freq_no == 3:
              peakfiles = t1_list3

        if t1_t2 == 2:
            if freq_no == 1:
              peakfiles = t2_list
            if freq_no == 2:
              peakfiles = t2_list2
            if freq_no == 3:
              peakfiles = t2_list3

        #create unresolved file
        unres = replace(unres, ",","\n")
        filename2 = target_dir + '/unresolved'
        file = open(filename2, 'w')
        file.write(unres)
        file.close()

        pipename = 'Tx ' + str(time.asctime(time.localtime()))

        # Create the NOE data pipe.
        pipe.create(pipename, 'relax_fit')

        # Load the backbone amide 15N spins from a PDB file.
        structure.read_pdb(str(structure_pdb))
        structure.load_spins(spin_id='@N')

        # Spectrum names.
        names = peakfiles

        # Relaxation times (in seconds).
        times = relax_times

        # Loop over the spectra.
        for i in xrange(len(names)):
            # Load the peak intensities.
            spectrum.read_intensities(file=names[i], spectrum_id=names[i], int_method='height')

            # Set the relaxation times.
            relax_fit.relax_time(time=float(times[i]), spectrum_id=names[i])

        # Specify the duplicated spectra.
        for i in range(0,(len(names))):
            for j in range(i,(len(names))):
               if relax_times[i] == times[j]:
                  if not i == j:   
                     spectrum.replicated(spectrum_ids=[names[i], names[j]])


        # Peak intensity error analysis.
        spectrum.error_analysis()
        
        # Deselect unresolved spins.
        deselect.read(file=resultsdir + '/unresolved')
        
        # Set the relaxation curve type.
        relax_fit.select_model('exp')
        
        # Grid search.
        grid_search(inc=11)
        
        # Minimise.
        minimise('simplex', scaling=False, constraints=False)
        
        # Monte Carlo simulations.
        monte_carlo.setup(number=500)
        monte_carlo.create_data()
        monte_carlo.initial_values()
        minimise('simplex', scaling=False, constraints=False)
        monte_carlo.error_analysis()
        
        # Save the relaxation rates.
        value.write(param='rx', file= savefile, force=True)
        
        
        # Create Grace plots of the data.
        grace.write(y_data_type='chi2', file='chi2.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Minimised chi-squared value.
        grace.write(y_data_type='i0', file='i0.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Initial peak intensity.
        grace.write(y_data_type='rx', file='rx.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Relaxation rate.
        grace.write(x_data_type='relax_times', y_data_type='int', file='intensities.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Average peak intensities.
        grace.write(x_data_type='relax_times', y_data_type='int', norm=True, file='intensities_norm.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Average peak intensities (normalised).
        
        
        
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

        msgbox(msg='T' + str(t1_t2) +' calculation was successfull !', title='relaxGUI ', ok_button='OK', image=sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif', root=None)

        # list files to results
        self.list_tx.Append(target_dir + '/grace/rx.' + str(nmr_freq) + '.agr')
        self.list_tx.Append(target_dir + '/grace/intensities_norm.' + str(nmr_freq) + '.agr')

        # add files to model-free tab
        if t1_t2 == 1:
                    if freqno == 1:
                      self.m_r1_1.SetValue(target_dir + '/r1.' + str(nmr_freq) + '.out')
                    if freqno == 2:
                      self.m_r1_2.SetValue(target_dir + '/r1.' + str(nmr_freq) + '.out')
                    if freqno == 3:
                      self.m_r1_3.SetValue(target_dir + '/r1.' + str(nmr_freq) + '.out')
        if t1_t2 == 2:
                    if freqno == 1:
                      self.m_r2_1.SetValue(target_dir + '/r2.' + str(nmr_freq) + '.out')
                    if freqno == 2:
                      self.m_r2_2.SetValue(target_dir + '/r2.' + str(nmr_freq) + '.out')
                    if freqno == 3:
                      self.m_r2_3.SetValue(target_dir + '/r2.' + str(nmr_freq) + '.out')
