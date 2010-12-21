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
from time import sleep
if dep_check.wx_module:
    import wx

# relax module imports.
from relax_errors import RelaxError
from relax_gui import Main

# relax GUI module imports.
from paths import IMAGE_PATH


__all__ = ['about',
           'base_classes',
           'controller',
           'derived_wx_classes',
           'filedialog',
           'menu',
           'message',
           'misc',
           'paths',
           'references',
           'relax_gui',
           'relax_prompt',
           'settings']



class App(wx.App):
    """The relax GUI wx application."""

    def OnInit(self):
        """Build the application, showing a splash screen first."""

        # Show the splash screen.
        self.show_splash()

        # Build the GUI.
        main = Main(parent=None, id=-1, title="")

        # Make it the main application component.
        self.SetTopWindow(main)

        # Wait a little while :)
        sleep(1)

        # Show it.
        main.Show()

        # All is good!
        return True


    def show_splash(self):
        """Build and show the splash screen."""

        # The image.
        bmp = wx.Bitmap(IMAGE_PATH+'start_no_alpha.png', wx.BITMAP_TYPE_ANY)

        # The timeout (ms).
        timeout = 2500

        # The splash screen.
        screen = wx.SplashScreen(bmp, wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT, timeout, None, -1)
