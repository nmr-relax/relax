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

# relaxGUI module import
from results_analysis import color_code_noe
from message import relax_run_ok

 
def make_rx(target_dir, rx_list, relax_times, structure_pdb, nmr_freq, r1_r2, freq_no, unres, self, freqno, global_setting, file_setting, sequencefile):

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
        savefile = str(target_dir) + sep + 'r' + str(r1_r2) + '.' + str(nmr_freq)  + '.out'


        # Select Peak Lists and Relaxation Times 
        peakfiles = rx_list

        if r1_r2 == 2:
            if freq_no == 1:
              peakfiles = r2_list
            if freq_no == 2:
              peakfiles = r2_list2
            if freq_no == 3:
              peakfiles = r2_list3

        #create unresolved file
        if not unres == '':
           print "\nCreating unresolved file"
           unres = replace(unres, ",","\n")
           unres = replace(unres, " ","")
           filename2 = target_dir + sep + 'unresolved'
           file = open(filename2, 'w')
           file.write(unres)
           file.close()

        pipename = 'Rx ' + str(time.asctime(time.localtime()))

        # Create the NOE data pipe.
        pipes.create(pipename, 'relax_fit')

        # Load Sequence
        if str(structure_pdb) == '!!! Sequence file selected !!!':
            
             # Read sequence file
             print "Reading Suquence from "+ sequencefile
             sequence.read(sequencefile)
        
        else:
             # Load the backbone amide 15N spins from a PDB file.
             print "\nReading sequence from " + str(structure_pdb)
             generic_fns.structure.main.read_pdb(str(structure_pdb))
             generic_fns.structure.main.load_spins(spin_id='@N')

        # Spectrum names.
        names = peakfiles

        # Relaxation times (in seconds).
        times = relax_times

        # Loop over the spectra.
        print '\n'
        for i in xrange(len(names)):
            # Load the peak intensities.
            print "\nspectrum.read(file=str("+names[i]+"), spectrum_id=str("+names[i]+"), int_method='height', heteronuc="+str(hetero)+", proton="+str(prot)+")"
            spectrum.read(file=str(names[i]), spectrum_id=str(names[i]), int_method='height', heteronuc=hetero, proton=prot)

            # Set the relaxation times.
            print "\nrelax_fit_obj._relax_time(time=float("+times[i]+"), spectrum_id="+names[i]+")"
            relax_fit_obj._relax_time(time=float(times[i]), spectrum_id=names[i])

        # Specify the duplicated spectra.
        print '\n'
        for i in range(0,(len(names))):
            for j in range(i,(len(names))):
               if times[i] == times[j]:
                  if not i == j:
                     print "spectrum.replicated(spectrum_ids=[" + names[i] + ", "+names[j]+"])"   
                     spectrum.replicated(spectrum_ids=[names[i], names[j]])


        # Peak intensity error analysis.
        print "spectrum.error_analysis()"
        spectrum.error_analysis()
        
        # Deselect unresolved spins.
        if not unres == '':
           print '\nDeselect Residues'
           selection.desel_read(file=resultsdir + sep + 'unresolved', res_num_col= 1)

        # Set the relaxation curve type.
        print "\nrelax_fit_obj._select_model('exp')"
        relax_fit_obj._select_model('exp')
        
        # Grid search.
        print "\nminimise.grid_search(inc=11)"
        minimise.grid_search(inc=11)
        
        # Minimise.
        print "minimise.minimise(min_algor='simplex', min_options=6, func_tol=1e-25, grad_tol=None, max_iterations=10000000, constraints=False, scaling=False, verbosity=1)"
        minimise.minimise(min_algor='simplex', min_options=6, func_tol=1e-25, grad_tol=None, max_iterations=10000000, constraints=False, scaling=False, verbosity=1)
        
        # Monte Carlo simulations.
        print "\nmonte_carlo.setup(number=500)"
        monte_carlo.setup(number=500)

        print "\nmonte_carlo.create_data('back_calc')"
        monte_carlo.create_data('back_calc')
 
        print "\nmonte_carlo.initial_values()"
        monte_carlo.initial_values()

        print "minimise.minimise(min_algor='simplex', min_options=6, func_tol=1e-25, grad_tol=None, max_iterations=10000000, constraints=False, scaling=False, verbosity=1)"
        minimise.minimise(min_algor='simplex', min_options=6, func_tol=1e-25, grad_tol=None, max_iterations=10000000, constraints=False, scaling=False, verbosity=1)

        print "\nmonte_carlo.error_analysis(prune= 0.0)"
        monte_carlo.error_analysis(prune= 0.0)
        
        # Save the relaxation rates.
        print "\nSaving Files:"
        value.write(param='rx', file= savefile, force=True)
        
        
        # Create Grace plots of the data.
        grace.write(y_data_type='chi2', file='chi2.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Minimised chi-squared value.
        grace.write(y_data_type='i0', file='i0.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Initial peak intensity.
        grace.write(y_data_type='rx', file='r' + str(r1_r2)+'.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Relaxation rate.
        grace.write(x_data_type='relax_times', y_data_type='int', file='intensities.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Average peak intensities.
        grace.write(x_data_type='relax_times', y_data_type='int', norm=True, file='intensities_norm.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Average peak intensities (normalised).
        
        
        
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

        # list files to results
        self.list_rx.Append(target_dir + sep + 'grace' + sep + 'r' + str(r1_r2)+'.' + str(nmr_freq) + '.agr')
        self.list_rx.Append(target_dir + sep + 'grace' + sep + 'intensities_norm.' + str(nmr_freq) + '.agr')

        # add files to model-free tab
        if r1_r2 == 1:
                    if freqno == 1:
                      self.m_r1_1.SetValue(target_dir + sep + 'r1.' + str(nmr_freq) + '.out')
                    if freqno == 2:
                      self.m_r1_2.SetValue(target_dir + sep + 'r1.' + str(nmr_freq) + '.out')
                    if freqno == 3:
                      self.m_r1_3.SetValue(target_dir + sep + 'r1.' + str(nmr_freq) + '.out')
        if r1_r2 == 2:
                    if freqno == 1:
                      self.m_r2_1.SetValue(target_dir + sep + 'r2.' + str(nmr_freq) + '.out')
                    if freqno == 2:
                      self.m_r2_2.SetValue(target_dir + sep + 'r2.' + str(nmr_freq) + '.out')
                    if freqno == 3:
                      self.m_r2_3.SetValue(target_dir + sep + 'r2.' + str(nmr_freq) + '.out')

        # Feedback
        relax_run_ok('T' + str(r1_r2) +' calculation was successful !') 
