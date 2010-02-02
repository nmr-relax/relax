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

# Package docstring.
"""Package for the Bieri GUI interface for relax.

This GUI was announced in the post at https://mail.gna.org/public/relax-devel/2009-11/msg00005.html.
"""

# Deps.
import dep_check

# Python module imports.
import sys
if dep_check.wx_module:
    import wx

# relax module imports.
from relax_errors import RelaxError
from relax_gui import show_about_gui, Main


__all__ = ['relax_gui']

# Execute the GUI.
def run(intro_string):
    """Build the Bieri GUI for relax.

    @param intro_string:    The relax introduction string.
    @type intro_string:     str
    """

    # Print the program intro.
    sys.stdout.write("%s\n" % intro_string)

    # Print the GUI intro.
    sys.stdout.write('\n\n\n\n\n')
    sys.stdout.write('##############################################\n')
    sys.stdout.write('#                                            #\n')
    sys.stdout.write('#  relaxGUI - graphical interface for relax  #\n')
    sys.stdout.write('#        (C) 2009 Michael Bieri              #\n')
    sys.stdout.write('#                                            #\n')
    sys.stdout.write('##############################################\n')
    sys.stdout.write('\n\n\n\n')

    # start wx Application
    relaxGUI = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()

    # show about panel
    show_about_gui()

    # Dependency check.
    if not dep_check.wx_module:
        sys.stderr.write("Please install the wx Python module to access the Bieri GUI.\n\n")
        sys.exit()

    # Build the GUI.
    relaxGUI_main = Main(parent=None, id=-1, title="")
    relaxGUI.SetTopWindow(relaxGUI_main)
    relaxGUI_main.Show()
    relaxGUI.MainLoop()
