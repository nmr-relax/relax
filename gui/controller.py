###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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

# Module docstring.
"""Log window of relax GUI controlling all calculations."""

# Python module imports.
import sys
import time
import wx

# relax module imports.
from status import Status; status = Status()

# relax GUI module imports.
from gui.icons import relax_icons
from gui.paths import IMAGE_PATH
from message import question


class Controller(wx.Frame):
    """The relax controller window."""

    def __init__(self, *args, **kwds):
        """Set up the relax controller frame."""

        # Create GUI elements
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        # Some default values.
        self.size_x = 600
        self.size_y = 600
        self.border = 5

        # IO redirection.
        if not status.debug and not status.test_mode:
            redir = Redirect_text(self)
            sys.stdout = redir
            sys.stderr = redir

        # Set up the frame.
        sizer = self.setup_frame()

        # Add the relax logo.
        self.add_relax_logo(sizer)

        # Add the header for the log.
        self.add_log_header(sizer)

        # Add the log panel.
        self.add_log(sizer)

        # Add the progress bar.
        self.add_progress(sizer)

        # Add the buttons.
        self.add_buttons(sizer)


    def add_buttons(self, sizer):
        """Add the buttons to the sizer.

        @param sizer:   The sizer element to pack the buttons into.
        @type sizer:    wx.Sizer instance
        """

        # Create a horizontal layout for the buttons.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, self.border)

        # The cancel button.
        cancel_button = wx.Button(self, -1, "Kill and Exit")
        cancel_button.SetToolTipString("Abort relax calculation")
        button_sizer.Add(cancel_button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.cancel_calculation, cancel_button)

        # The close button.
        close_button = wx.Button(self, -1, "Close")
        close_button.SetToolTipString("Close log window")
        button_sizer.Add(close_button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.handler_close, close_button)


    def add_log(self, sizer):
        """Add the log panel to the sizer.

        @param sizer:   The sizer element to pack the log panel into.
        @type sizer:    wx.Sizer instance
        """

        # Log panel
        self.log_panel = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY)

        # Set the font info.
        self.log_panel.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL, 0, ""))

        # Add to the sizer.
        sizer.Add(self.log_panel, 1, wx.EXPAND|wx.ALL, self.border)


    def add_log_header(self, sizer):
        """Add the log header to the sizer.

        @param sizer:   The sizer element to pack the log header into.
        @type sizer:    wx.Sizer instance
        """

        # The log header text.
        header_log = wx.StaticText(self, -1, "", style=wx.ALIGN_CENTRE)

        # Set the minimum size.
        header_log.SetSize((self.size_x, 18))

        # Set the font info.
        header_log.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

        # Add to the sizer.
        sizer.Add(header_log, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)


    def add_progress(self, sizer):
        """Add the progress bar to the sizer.

        @param sizer:   The sizer element to pack the progress bar into.
        @type sizer:    wx.Sizer instance
        """

        # The progress bar.
        self.progress_bar = wx.Gauge(self, -1, 100)

        # Set the size of the progress bar.
        self.progress_bar.SetSize((self.size_x - 2*self.border, 20))

        # Add the progress bar.
        sizer.Add(self.progress_bar, 0, wx.EXPAND|wx.ALL, self.border)


    def add_relax_logo(self, sizer):
        """Add the relax logo to the sizer.

        @param sizer:   The sizer element to pack the relax logo into.
        @type sizer:    wx.Sizer instance
        """

        # The logo.
        logo = wx.StaticBitmap(self, -1, wx.Bitmap(IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))

        # Add the relax logo.
        sizer.Add(logo, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, self.border)


    def cancel_calculation(self, event):
        """Abort the calculations.

        This currently does nothing!

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask if the user is sure they would like to exit.
        doexit = question('Are you sure you would like to kill your current relax session?  All unsaved data will be lost.', default=True)

        # Kill session.
        if doexit:
            sys.exit(0)


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close the window.
        self.Hide()


    def setup_frame(self):
        """Set up the relax controller frame.
        @return:    The sizer object.
        @rtype:     wx.Sizer instance
        """

        # Set the frame title.
        self.SetTitle("The relax controller")

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # Use a grid sizer for packing the elements.
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Pack the sizer into the frame.
        self.SetSizer(main_sizer)

        # Close the window cleanly (hide so it can be reopened).
        self.Bind(wx.EVT_CLOSE, self.handler_close)

        # Set the default size of the controller.
        self.SetSize((self.size_x, self.size_y))

        # Centre the frame.
        self.Centre()

        # Return the sizer.
        return main_sizer



class Redirect_text(object):
    """Class to redirect relax output to relaxGUI - log panel and progress bar."""

    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl


    def limit_entries(self):
        """ Function to overcome feedback problem of wx.CallAfter() command"""

        # Maximum allowed number of lines in log window.
        max_entries = 10000

        # read number of lines in log window.
        total_entries = self.out.log_panel.GetNumberOfLines()

        # Shift entries backwards if maximum of line exeeded.
        if total_entries > max_entries:
            # Reset log window entries
            new_entries = 'Refreshing log window...\n\n'
            self.out.log_panel.SetValue(new_entries)

    def write(self, string):

        # Limit panle entries to max_entries Lines.
        wx.CallAfter(self.limit_entries)

        # Update Gauge (Progress bar).
        # Local tm model:
        if status.dAuvergne_protocol.diff_model == 'local_tm':
            if status.dAuvergne_protocol.current_model:
                # Current model.
                no = status.dAuvergne_protocol.current_model[2:]
                no = int(no)

                # Total selected models.
                total_models = len(status.dAuvergne_protocol.local_tm_models)

                # update Progress bar.
                wx.CallAfter(self.out.progress_bar.SetValue, (100*no/total_models))

        # Sphere to Ellipsoid Models.
        elif status.dAuvergne_protocol.diff_model in ['sphere', 'prolate', 'oblate', 'ellipsoid']:
            # Determine actual round (maximum is 20).
            wx.CallAfter(self.out.progress_bar.SetValue, (100*(status.dAuvergne_protocol.round-1)/20))

        # Final analysis or Rx calculation.
        else:
            if status.mc_number:
                progress = 100 * (status.mc_number+2) / cdp.sim_number
                wx.CallAfter(self.out.progress_bar.SetValue, progress)

        # Add new output.
        wx.CallAfter(self.out.log_panel.AppendText, string)
        time.sleep(0.001)  # allow relaxGUI log panel to get refreshed


class Thread_container:
    """Storage object for the calculation threads."""
