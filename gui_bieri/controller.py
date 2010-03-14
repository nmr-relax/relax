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

# Module docstring.
"""Log window of relax GUI controlling all calculations."""

# Python module imports.
from os import sep
from string import split, replace
import sys
import time
import thread
import wx

# relaxGUI module imports.
from gui_bieri.execution.calc_noe import make_noe
from gui_bieri.execution.calc_rx import make_rx
from gui_bieri.paths import IMAGE_PATH


class Controller(wx.Dialog):
    """The relax controller window."""

    def __init__(self, *args, **kwds):

        # Create GUI elements
        kwds["style"] = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX
        wx.Dialog.__init__(self, *args, **kwds)

        # header
        self.relax_logo = wx.StaticBitmap(self, -1, wx.Bitmap(IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))
        self.header_log = wx.StaticText(self, -1, "", style=wx.ALIGN_CENTRE)

        # Log panel
        self.log_panel = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY)

        # progress bar
        self.progress_bar = wx.Gauge(self, -1, 100)

        # buttons
        self.cancel_button = wx.Button(self, -1, "Cancel")
        self.close_button = wx.Button(self, -1, "Close")

        # Create Objects (see below)
        self.__set_properties()
        self.__do_layout()

        # Button actions
        self.Bind(wx.EVT_BUTTON, self.cancel_calculation, self.cancel_button)
        self.Bind(wx.EVT_BUTTON, self.handler_close, self.close_button)

        # Start Calculation in Thread
        #if WHICH_CALC == 'Rx':
        #    thread.start_new_thread(make_rx, (PARAMETERS[0], PARAMETERS[1], PARAMETERS[2], PARAMETERS[3], PARAMETERS[4], PARAMETERS[5], PARAMETERS[6], PARAMETERS[7], PARAMETERS[8], PARAMETERS[9], PARAMETERS[10], PARAMETERS[11], PARAMETERS[12]))

        #if WHICH_CALC == 'Noe':
        #    thread.start_new_thread(make_noe, (PARAMETERS[0], PARAMETERS[1], PARAMETERS[2], PARAMETERS[3], PARAMETERS[4], PARAMETERS[5], PARAMETERS[6], PARAMETERS[7], PARAMETERS[8], PARAMETERS[9], PARAMETERS[10], PARAMETERS[11], PARAMETERS[12], PARAMETERS[13]))


    def __do_layout(self):

        # create the lay out
        main_sizer = wx.FlexGridSizer(5, 1, 0, 0)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.relax_logo, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 5)
        main_sizer.Add(self.header_log, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
        main_sizer.Add(self.log_panel, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        main_sizer.Add(self.progress_bar, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        button_sizer.Add(self.cancel_button, 0, wx.ADJUST_MINSIZE, 0)
        button_sizer.Add(self.close_button, 0, wx.ADJUST_MINSIZE, 0)
        main_sizer.Add(button_sizer, 5, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(main_sizer)
        self.Layout()
        self.SetSize((600, 600))


    def __set_properties(self):

        # properties of GUI elements (used at start up)
        self.SetTitle("relaxGUI - Log Window")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((600, 600))
        self.header_log.SetMinSize((600, 18))
        self.header_log.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.log_panel.SetMinSize((590, 410))
        self.progress_bar.SetMinSize((590, 20))
        self.cancel_button.SetToolTipString("Abort relax calculation")
        self.close_button.SetToolTipString("Close log window")


    def cancel_calculation(self, event):
        """Abort the calculations.

        This currently does nothing!

        @param event:   The wx event.
        @type event:    wx event
        """

        # Terminate the event.
        event.Skip()


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close the window.
        self.Close()

        # Terminate the event.
        event.Skip()



class Redirect_text(object):
    """Class to redirect relax output to relaxGUI - log panel and progress bar."""

    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl


    def write(self,string):
        global progress

        # Limit panle entries to max_entries Lines.
        wx.CallAfter(self.limit_entries)

        # Add new output.
        wx.CallAfter(self.out.log_panel.AppendText, string)
        time.sleep(0.001)  # allow relaxGUI log panel to get refreshed


class Thread_container:
    """Storage object for the calculation threads."""
