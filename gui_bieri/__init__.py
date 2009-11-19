###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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

# Deps.
import dep_check

# Python module imports.
import sys
if dep_check.wx_module:
    import wx

# relax module imports.
from relax_errors import RelaxError
from relax_gui import main


__all__ = ['relax_gui']

__doc__ = \
"""Package for the Bieri GUI interface for relax.

This GUI was announced in the post at https://mail.gna.org/public/relax-devel/2009-11/msg00005.html.
"""

# Execute the GUI.
def run():
    """Build the Bieri GUI for relax."""

    # Dependency check.
    if not dep_check.wx_module:
        sys.stderr.write("Please install the wx Python module to access the Bieri GUI.\n\n")
        sys.exit()

    # Build the GUI.
    relaxGUI = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    relaxGUI_main = main(None, -1, "")
    relaxGUI.SetTopWindow(relaxGUI_main)
    relaxGUI_main.Show()
    relaxGUI.MainLoop()
