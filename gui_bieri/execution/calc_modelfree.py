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

# script to calculate model-free models

# Python module imports.
import math
from os import listdir, sep
from re import search
from string import replace
import time
import wx

# relax module imports.
from auto_analyses.dauvergne_protocol import dAuvergne_protocol
from float import floatAsByteArray
from generic_fns import diffusion_tensor, eliminate, fix, grace, minimise, model_selection, monte_carlo, pipes, relax_data, results, selection, sequence, spectrum, value
from generic_fns.mol_res_spin import generate_spin_id, spin_index_loop, spin_loop
import generic_fns.structure.main
from relax_errors import RelaxError
from specific_fns.setup import model_free_obj

# relaxGUI module imports.
from gui_bieri.message import relax_run_ok


def convert_to_float(string):
    """Method to convert a string like '1.02*1e-10' to a float variable.

    @param string:  The number in string form.
    @type string:   str
    @return:        The floating point number.
    @rtype:         float
    """

    # Break the number up.
    entries = string.split('*')

    # The first part of the number.
    a = entries[0]
    a = float(a)

    # The second part of the number.
    b = entries[1]
    b = float(b[2:len(b)])

    # Recombine.
    result = a * math.pow(10, b)

    # Return the float.
    return result


class RedirectText(object):
    """Class to redirect relax output to relaxGUI - log panel and progress bar."""

    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

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
