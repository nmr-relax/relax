###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Edward d'Auvergne                                   #
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
from status import Status; status = Status()

# relax GUI module imports.
from paths import IMAGE_PATH


__all__ = ['about',
           'base_classes',
           'controller',
           'derived_wx_classes',
           'errors',
           'filedialog',
           'fonts',
           'icons',
           'interpreter',
           'menu',
           'message',
           'misc',
           'paths',
           'pipe_editor',
           'references',
           'relax_gui',
           'relax_prompt',
           'settings',
           'wizard']



class App(wx.App):
    """The relax GUI wx application."""

    def __init__(self, script=None, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        """Initialise the wx.App.

        @keyword redirect:      Should sys.stdout and sys.stderr be redirected? Defaults to True on Windows and Mac, False otherwise. If filename is None then output will be redirected to a window that pops up as needed. (You can control what kind of window is created for the output by resetting the class variable outputWindowClass to a class of your choosing.)
        @type redirect:         bool
        @keyword filename:      The name of a file to redirect output to, if redirect is True.
        @type filename:         file object
        @keyword useBestVisual: Should the app try to use the best available visual provided by the system (only relevant on systems that have more than one visual.) This parameter must be used instead of calling SetUseBestVisual later on because it must be set before the underlying GUI toolkit is initialized.
        @type useBestVisual:    bool
        @keyword clearSigInt:   Should SIGINT be cleared? This allows the app to terminate upon a Ctrl-C in the console like other GUI apps will.
        @type clearSigInt:      bool
        @keyword script:        The path of a relax script to execute.
        @type script:           str
        """

        # Store the script.
        self.script = script

        # Execute the base class method.
        super(App, self).__init__(redirect=redirect, filename=filename, useBestVisual=useBestVisual, clearSigInt=clearSigInt)


    def OnInit(self, script_file=None):
        """Build the application, showing a splash screen first."""

        # Show the splash screen.
        self.show_splash()

        # Build the GUI.
        self.gui = Main(parent=None, id=-1, title="", script=self.script)

        # Make it the main application component.
        self.SetTopWindow(self.gui)

        # Only show the GUI if requested.
        if status.show_gui:
            # Wait a little while :)
            sleep(1)

            # Show it.
            self.gui.Show()

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
