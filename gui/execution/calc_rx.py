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
from string import replace
import sys
import time
import wx

# relax module imports.
from generic_fns import monte_carlo, results, minimise, pipes, sequence, spectrum, selection, value, grace, state
import generic_fns.structure.main
from specific_fns.setup import relax_fit_obj


def make_rx(target_dir, rx_list, relax_times, structure_pdb, nmr_freq, r1_r2, freq_no, unres, main, freqno, global_setting, file_setting, sequencefile, self):
    """Rx calculation."""

    # Number of Monte Carlo simulations
    global montecarlo
    montecarlo = int(global_setting[6])

    # value for progress bar during monte carlo simulation
    global progress
    progress = 5.0

    # redirect relax output and errors to relaxGUI - log panel
    redir = RedirectText(self)
    sys.stdout = redir
    sys.stderr = redir

    hetero = global_setting[2]
    prot = global_setting[3]
    resultsdir = str(target_dir)
    gracedir = str(target_dir) + sep + 'grace'
    savefile = str(target_dir) + sep + 'r' + str(r1_r2) + '.' + str(nmr_freq) + '.out'

    wx.CallAfter(self.log_panel.AppendText, ('Starting R' + str(r1_r2) + ' calculation\n------------------------------------------\n\n') )
    time.sleep(0.5)

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
        wx.CallAfter(self.log_panel.AppendText, ('Creating unresolved file\n\n'))
        time.sleep(0.001)
        unres = replace(unres, ",", "\n")
        unres = replace(unres, " ", "")
        filename2 = target_dir + sep + 'unresolved'
        file = open(filename2, 'w')
        file.write(unres)
        file.close()

    pipename = 'Rx ' + str(time.asctime(time.localtime()))

    # Create the NOE data pipe.
    wx.CallAfter(self.log_panel.AppendText, ("pipes.create("+pipename+", 'relax_fit')\n\n"))
    time.sleep(0.001)
    pipes.create(pipename, 'relax_fit')

    # update progress bar
    wx.CallAfter(self.progress_bar.SetValue, (1))

    # Load Sequence
    if str(structure_pdb) == '!!! Sequence file selected !!!':
        # Read sequence file
        wx.CallAfter(self.log_panel.AppendText, ("Reading Suquence from "+ sequencefile+'\n\n'))
        time.sleep(0.001)
        sequence.read(sequencefile)

    else:
        # Load the backbone amide 15N spins from a PDB file.
        wx.CallAfter(self.log_panel.AppendText, ("Reading sequence from " + str(structure_pdb) + '\n\n'))
        generic_fns.structure.main.read_pdb(str(structure_pdb))
        generic_fns.structure.main.load_spins(spin_id='@N')

    # update progress bar
    wx.CallAfter(self.progress_bar.SetValue, (2))

    # Spectrum names.
    names = peakfiles

    # Relaxation times (in seconds).
    times = relax_times

    # Loop over the spectra.
    print '\n'
    for i in xrange(len(names)):
        # Load the peak intensities.
        wx.CallAfter(self.log_panel.AppendText, ("spectrum.read(file=str("+names[i]+"), spectrum_id=str("+names[i]+"), int_method='height', heteronuc="+str(hetero)+", proton="+str(prot)+")\n\n"))
        spectrum.read(file=str(names[i]), spectrum_id=str(names[i]), int_method='height', heteronuc=hetero, proton=prot)

        # Set the relaxation times.
        print "\nrelax_fit_obj._relax_time(time=float("+times[i]+"), spectrum_id="+names[i]+")"
        relax_fit_obj._relax_time(time=float(times[i]), spectrum_id=names[i])

    # Specify the duplicated spectra.
    print '\n'
    for i in range(0, (len(names))):
        for j in range(i, (len(names))):
            if times[i] == times[j]:
                if not i == j:
                    print "spectrum.replicated(spectrum_ids=[" + str(names[i]) + ", "+str(names[j])+"])"
                    spectrum.replicated(spectrum_ids= [ str(names[i]), str(names[j])])

    # update progress bar
    wx.CallAfter(self.progress_bar.SetValue, (4))

    # Peak intensity error analysis.
    print "spectrum.error_analysis()"
    spectrum.error_analysis()

    # Deselect unresolved spins.
    if not unres == '':
        print '\nDeselect Residues'
        selection.desel_read(file=resultsdir + sep + 'unresolved', res_num_col= 1)

    # update progress bar
    wx.CallAfter(self.progress_bar.SetValue, (5))

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
    print "\nmonte_carlo.setup(number="+str(montecarlo)+")"
    monte_carlo.setup(number=montecarlo)

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
    grace.write(y_data_type='chi2', file='chi2.' + str(nmr_freq) + '.agr', dir=gracedir, force=True)    # Minimised chi-squared value.
    grace.write(y_data_type='i0', file='i0.' + str(nmr_freq) + '.agr', dir=gracedir, force=True)    # Initial peak intensity.
    grace.write(y_data_type='rx', file='r' + str(r1_r2)+'.' + str(nmr_freq) + '.agr', dir=gracedir, force=True)    # Relaxation rate.
    grace.write(x_data_type='relax_times', y_data_type='int', file='intensities.' + str(nmr_freq) + '.agr', dir=gracedir, force=True)    # Average peak intensities.
    grace.write(x_data_type='relax_times', y_data_type='int', norm=True, file='intensities_norm.' + str(nmr_freq) + '.agr', dir=gracedir, force=True)    # Average peak intensities (normalised).

    # Write the results.
    results.write(file='results', directory=resultsdir, force=True)

    # Save the program state.
    state.save_state('save', dir=resultsdir, force=True)

    print ""
    print ""
    print ""
    print "________________________________________________________________________________"
    print ""
    print "calculation finished"
    print "________________________________________________________________________________"

    # list files to results
    main.list_rx.Append(target_dir + sep + 'grace' + sep + 'r' + str(r1_r2)+'.' + str(nmr_freq) + '.agr')
    main.list_rx.Append(target_dir + sep + 'grace' + sep + 'intensities_norm.' + str(nmr_freq) + '.agr')

    # add files to model-free tab
    if r1_r2 == 1:
        if freqno == 1:
            main.m_r1_1.SetValue(target_dir + sep + 'r1.' + str(nmr_freq) + '.out')
        if freqno == 2:
            main.m_r1_2.SetValue(target_dir + sep + 'r1.' + str(nmr_freq) + '.out')
        if freqno == 3:
            main.m_r1_3.SetValue(target_dir + sep + 'r1.' + str(nmr_freq) + '.out')
    if r1_r2 == 2:
        if freqno == 1:
            main.m_r2_1.SetValue(target_dir + sep + 'r2.' + str(nmr_freq) + '.out')
        if freqno == 2:
            main.m_r2_2.SetValue(target_dir + sep + 'r2.' + str(nmr_freq) + '.out')
        if freqno == 3:
            main.m_r2_3.SetValue(target_dir + sep + 'r2.' + str(nmr_freq) + '.out')

    # update progress bar
    wx.CallAfter(self.progress_bar.SetValue, (100))

    # enable close button and disable cancel button
    wx.CallAfter(self.close_button.Enable, True)
    wx.CallAfter(self.cancel_button.Enable, False)

    # close thread
    return


class RedirectText(object):
    """Class to redirect relax output to relaxGUI - log panel and progress bar."""

    def __init__(self, aWxTextCtrl):
        self.out = aWxTextCtrl


    def write(self, string):
        global progress

        wx.CallAfter(self.out.log_panel.WriteText, string)
        time.sleep(0.001)  # allow relaxGUI log panel to get refreshed

        # split print out into list
        a = str(string)
        check = []
        check = a.split()

        # update progress bar
        if 'Simulation' in string:
            add = round(progress)
            add_int = int(add)
            wx.CallAfter(self.out.progress_bar.SetValue, add_int)
            progress = ( (int(check[1]) * 100) / float(montecarlo + 6)) + 5
            time.sleep(0.001)  # allow relaxGUI progressbar to get refreshed
