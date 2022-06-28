###############################################################################
#                                                                             #
# Copyright (C) 2009-2012,2022 Edward d'Auvergne                              #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Package docstring.
"""Package for the Bieri GUI interface for relax.

This GUI was announced in the post at U{https://web.archive.org/web/https://mail.gna.org/public/relax-devel/2009-11/msg00005.html}.
"""

# Deps.
import dep_check

# Python module imports.
import sys
from time import sleep
if dep_check.wx_module:
    import wx
    if not dep_check.wx_classic:
        import wx.adv

# relax module imports.
from graphics import IMAGE_PATH
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from lib.errors import RelaxError
import pipe_control
from status import Status; status = Status()


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


# Size for the splash screen.
SPLASH_SIZE = (640, 460)



class App(wx.App):
    """The relax GUI wx application."""

    def __init__(self, script_file=None, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        """Initialise the wx.App.

        @keyword redirect:      Should sys.stdout and sys.stderr be redirected? Defaults to True on Windows and Mac, False otherwise. If filename is None then output will be redirected to a window that pops up as needed. (You can control what kind of window is created for the output by resetting the class variable outputWindowClass to a class of your choosing.)
        @type redirect:         bool
        @keyword filename:      The name of a file to redirect output to, if redirect is True.
        @type filename:         file object
        @keyword useBestVisual: Should the app try to use the best available visual provided by the system (only relevant on systems that have more than one visual.) This parameter must be used instead of calling SetUseBestVisual later on because it must be set before the underlying GUI toolkit is initialized.
        @type useBestVisual:    bool
        @keyword clearSigInt:   Should SIGINT be cleared? This allows the app to terminate upon a Ctrl-C in the console like other GUI apps will.
        @type clearSigInt:      bool
        @keyword script_file:   The path of a relax script to execute.
        @type script_file:      str
        """

        # First run the script before the GUI is built.
        if script_file:
            pipe_control.script.script(script_file)

        # Execute the base class method.
        super(App, self).__init__(redirect=redirect, filename=filename, useBestVisual=useBestVisual, clearSigInt=clearSigInt)


    def OnInit(self):
        """Build the application, showing a splash screen first."""

        # Import here to break a circular import which is killing Epydoc!
        from gui import relax_gui

        # Build the GUI.
        self.gui = relax_gui.Main(parent=None, id=-1, title="")

        # Make it the main application component.
        self.SetTopWindow(self.gui)

        # Only show the GUI if requested.
        if status.show_gui:
            # Wait a little while :)
            sleep(1)

            # Show it.
            self.gui.Show()

        # Show the splash screen.
        splash = RelaxSplash(self.gui)
        splash.CenterOnScreen(wx.BOTH)

        # All is good!
        return True



class RelaxSplash(wx.Frame):
    """A special splash screen for the relax GUI."""

    def __init__(self, parent):
        """Set up the splash screen."""

        # Set up the frame.
        super(RelaxSplash, self).__init__(parent=parent, id=-1, title="RelaxSplash", size=SPLASH_SIZE, style=wx.FRAME_SHAPED | wx.BORDER_NONE | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP)
        self.SetBackgroundColour("white")

        self.Show(True)

        # Start the timer.
        self.timer = wx.Timer(self)
        self.timer.Start(4000)
        self.Bind(wx.EVT_TIMER, self.handler_timer, self.timer)

        # Set up the foreground and background panels.
        panel_bg = RelaxBackgroundPanel(self)
        panel_fg = RelaxForegroundPanel(self)

        # Main sizer.
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(panel_bg, 1, wx.EXPAND, 20)
        main_sizer.Add(panel_fg, 1, wx.EXPAND, 20)
        self.SetSizer(main_sizer)

        # Set the cursor as busy.
        wx.BeginBusyCursor()

        # Bind events.
        self.Bind(wx.EVT_LEFT_DOWN, self.mouse_events)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.mouse_events)
        self.Bind(wx.EVT_RIGHT_DOWN, self.mouse_events)


    def Destroy(self, event):
        """Override the class method."""

        # Stop the busy cursor.
        wx.CallAfter(wx.EndBusyCursor)

        # Stop the timer.
        self.timer.Stop()

        # Destroy the splash window.
        super(RelaxSplash, self).Destroy()


    def handler_timer(self, event):
        """Close the splash screen."""

        self.Destroy(event)


    def mouse_events(self, event):
        """Close the splash on mouse button clicks."""

        self.Destroy(event)
        event.Skip()



class RelaxBackgroundPanel(wx.Panel):
    """Custom panel for the animation part of the splash screen."""

    def __init__(self, parent=None):
        """Set up the custom panel."""

        # Initialise the parent.
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent

        # Animation.
        self.gif = wx.adv.Animation(IMAGE_PATH+'movie_mode1_relax.gif')
        ani_ctrl = wx.adv.AnimationCtrl(self, id=-1, anim=self.gif, size=(480,428))
        ani_ctrl.Play()

        # Layout.
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(10)
        sizer2.AddSpacer(20)
        sizer2.Add(ani_ctrl)
        sizer.Add(sizer2)
        self.SetSizerAndFit(sizer)
        self.Show()



class RelaxForegroundPanel(wx.Panel):
    """Custom panel for the bitmap part of the splash screen."""

    def __init__(self, parent=None):
        """Set up the custom panel."""

        # Initialise the parent.
        wx.Panel.__init__(self, parent, -1, style=wx.TRANSPARENT_WINDOW)
        self.parent = parent

        # Background image.
        bmp = wx.Bitmap(IMAGE_PATH+'relaxGUI_splash.png', wx.BITMAP_TYPE_ANY)
        image = wx.StaticBitmap(self, -1, bmp)

        # Layout.
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(image)
        self.SetSizerAndFit(sizer)

        # Send mouse clicks to the parent.
        image.Bind(wx.EVT_MOUSE_EVENTS, self.mouse_events)


    def mouse_events(self, event):
        """Send all mouse events to the parent."""

        wx.PostEvent(self.parent, event)
        event.Skip()
