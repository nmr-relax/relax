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
from os import sep
from string import replace
import sys
import time
import wx

# relax module imports.
from generic_fns import grace, minimise, pipes, results, selection, spectrum, state, value
import generic_fns.structure.main
from specific_fns.setup import noe_obj


def make_noe(target_dir, noe_ref, noe_sat, rmsd_ref, rmsd_sat, nmr_freq, struct_pdb, unres, execute, main, freqno, global_setting, file_setting, sequencefile, self):
    """NOE calculation."""

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
    save_file = str(target_dir) + sep + 'noe.' + str(nmr_freq) + '.out'
    noe_ref_1 = noe_ref
    noe_sat_1 = noe_sat
    unres = str(unres)

    wx.CallAfter(self.log_panel.AppendText, ('Starting NOE calculation\n------------------------------------------\n\n') )
    time.sleep(0.5)

    #create unresolved file
    if not unres == '':
        print "\nCreate unresolved file"
        unres = replace(unres, ",", "\n")
        unres = replace(unres, " ", "")
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
    grace.write(y_data_type='ref_spec', file='ref.' + str(nmr_freq) + '.agr', dir=gracedir, force=True)
    grace.write(y_data_type='sat_spec', file='sat.' + str(nmr_freq) + '.agr', dir=gracedir, force=True)
    grace.write(y_data_type='noe', file='noe.' + str(nmr_freq) + '.agr', dir=gracedir, force=True)

    # Write the results.
    results.write(file='results', directory=resultsdir, force=True)

    # Save the program state.
    state.save_state('save', dir = resultsdir, force=True)

    print ""
    print ""
    print ""
    print "________________________________________________________________________________"
    print ""
    print "calculation finished"
    print "________________________________________________________________________________"

    if freqno == 1:
        main.m_noe_1.SetValue(target_dir + sep + 'noe.' + str(nmr_freq) + '.out')
    if freqno == 2:
        main.m_noe_2.SetValue(target_dir + sep + 'noe.' + str(nmr_freq) + '.out')
    if freqno == 3:
        main.m_noe_3.SetValue(target_dir + sep + 'noe.' + str(nmr_freq) + '.out')
    main.list_noe.Append(target_dir + sep + 'grace' + sep + 'noe.' + str(nmr_freq) + '.agr')

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


    def write(self,string):
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
