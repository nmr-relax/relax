###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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
import wx
import sys


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.CLOSE_BOX|wx.STAY_ON_TOP
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self.panel_2 = wx.Panel(self, -1)
        self.bitmap_1 = wx.StaticBitmap(self.panel_1, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'start.png', wx.BITMAP_TYPE_ANY))
        self.button_1 = wx.Button(self, -1, "Ok")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.start, self.button_1)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("relaxGUI")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((640, 540))
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.panel_2.SetMinSize((640, 30))
        self.panel_2.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.panel_1.SetMinSize((640,480))
        self.panel_1.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.button_1.SetBackgroundColour(wx.Colour(50, 50, 50))
        self.button_1.SetForegroundColour(wx.Colour(0, 0, 0))
        self.button_1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.panel_2, 1, wx.EXPAND, 0)
        sizer_2.Add(self.bitmap_1, 0, 0, 0)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 0, wx.EXPAND, 0)
        sizer_1.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        self.Centre()
        # end wxGlade

    def start(self, event): # wxGlade: MyFrame.<event_handler>
        self.Close()
        event.Skip()

# end of class MyFrame


def about_relax():
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    start = MyFrame(None, -1, "")
    app.SetTopWindow(start)
    start.Show()
    app.MainLoop()
