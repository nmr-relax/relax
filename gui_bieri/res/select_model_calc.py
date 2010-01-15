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

import wx
import sys
from os import sep
import time

from message import missing_data

selection = None

class select_tensor(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin select_tensor.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_13 = wx.StaticText(self, -1, "Select Calculation Mode:")
        self.label_2_copy_copy_copy = wx.StaticText(self, -1, "Automatic")
        self.button_4_copy_copy = wx.Button(self, -1, "Full Analysis")
        self.label_7_copy_copy_copy = wx.StaticText(self, -1, "Local tm")
        self.button_2_copy_copy = wx.Button(self, -1, "Local tm")
        self.label_8_copy_copy = wx.StaticText(self, -1, "Sphere")
        self.bitmap_button_1_copy_copy = wx.BitmapButton(self, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'sphere.jpg', wx.BITMAP_TYPE_ANY))
        self.label_9_copy_copy_copy = wx.StaticText(self, -1, "Prolate")
        self.bitmap_button_2_copy_copy = wx.BitmapButton(self, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'prolate.jpg', wx.BITMAP_TYPE_ANY))
        self.label_10_copy_copy_copy = wx.StaticText(self, -1, "Oblate")
        self.bitmap_button_3_copy_copy = wx.BitmapButton(self, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'oblate.jpg', wx.BITMAP_TYPE_ANY))
        self.label_11_copy_copy_copy = wx.StaticText(self, -1, "Ellipsoid")
        self.bitmap_button_4_copy_copy = wx.BitmapButton(self, -1, wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'ellipsoid.jpg', wx.BITMAP_TYPE_ANY))
        self.label_12_copy_copy_copy = wx.StaticText(self, -1, "Final")
        self.button_3_copy_copy = wx.Button(self, -1, "Final")
        self.panel_2_copy = wx.Panel(self, -1)
        self.button_1_copy_copy_copy = wx.Button(self, -1, "Cancel")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.full, self.button_4_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.sphere, self.bitmap_button_1_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.prolate, self.bitmap_button_2_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.oblate, self.bitmap_button_3_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.ellipsoid, self.bitmap_button_4_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.final, self.button_3_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.cancel, self.button_1_copy_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.local, self.button_2_copy_copy)
        # end 

    def __set_properties(self):
        # begin  select_tensor.__set_properties
        self.SetTitle("relaxGUI")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.label_13.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_2_copy_copy_copy.SetMinSize((100, 29))
        self.button_4_copy_copy.SetMinSize((111, 29))
        self.label_7_copy_copy_copy.SetMinSize((100, 17))
        self.button_2_copy_copy.SetMinSize((111, 29))
        self.label_8_copy_copy.SetMinSize((100, 17))
        self.bitmap_button_1_copy_copy.SetSize(self.bitmap_button_1_copy_copy.GetBestSize())
        self.label_9_copy_copy_copy.SetMinSize((100, 17))
        self.bitmap_button_2_copy_copy.SetSize(self.bitmap_button_2_copy_copy.GetBestSize())
        self.label_10_copy_copy_copy.SetMinSize((100, 17))
        self.bitmap_button_3_copy_copy.SetSize(self.bitmap_button_3_copy_copy.GetBestSize())
        self.label_11_copy_copy_copy.SetMinSize((100, 17))
        self.bitmap_button_4_copy_copy.SetSize(self.bitmap_button_4_copy_copy.GetBestSize())
        self.label_12_copy_copy_copy.SetMinSize((100, 28))
        self.button_3_copy_copy.SetMinSize((111, 29))
        self.panel_2_copy.SetMinSize((100, 29))
        self.button_1_copy_copy_copy.SetMinSize((111, 29))
        # end 

    def __do_layout(self):
        # begin select_tensor.__do_layout
        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1_copy = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_9.Add(self.label_13, 0, wx.ALL, 5)
        grid_sizer_1_copy.Add(self.label_2_copy_copy_copy, 0, wx.LEFT|wx.TOP|wx.SHAPED, 5)
        grid_sizer_1_copy.Add(self.button_4_copy_copy, 0, 0, 0)
        grid_sizer_1_copy.Add(self.label_7_copy_copy_copy, 0, wx.LEFT|wx.EXPAND, 5)
        grid_sizer_1_copy.Add(self.button_2_copy_copy, 0, wx.SHAPED, 0)
        grid_sizer_1_copy.Add(self.label_8_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.bitmap_button_1_copy_copy, 0, wx.SHAPED, 0)
        grid_sizer_1_copy.Add(self.label_9_copy_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.bitmap_button_2_copy_copy, 0, wx.SHAPED, 0)
        grid_sizer_1_copy.Add(self.label_10_copy_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.bitmap_button_3_copy_copy, 0, wx.SHAPED, 0)
        grid_sizer_1_copy.Add(self.label_11_copy_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.bitmap_button_4_copy_copy, 0, 0, 0)
        grid_sizer_1_copy.Add(self.label_12_copy_copy_copy, 0, wx.LEFT|wx.SHAPED, 5)
        grid_sizer_1_copy.Add(self.button_3_copy_copy, 0, 0, 0)
        grid_sizer_1_copy.Add(self.panel_2_copy, 1, wx.EXPAND, 0)
        grid_sizer_1_copy.Add(self.button_1_copy_copy_copy, 0, 0, 0)
        sizer_9.Add(grid_sizer_1_copy, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_9)
        sizer_9.Fit(self)
        self.Layout()
        # end 

    def local(self, event): # local tm
        global selection
        selection = 'local_tm'
        self.Destroy()
        event.Skip()

    def full(self, event): # automatic
        global selection
        selection = 'full'
        self.Close()
        event.Skip()

    def sphere(self, event): # sphere
        global selection
        selection = 'sphere'
        self.Close()
        event.Skip()

    def prolate(self, event): # prolate
        global selection
        selection = 'prolate'
        self.Destroy()
        event.Skip()

    def oblate(self, event): # oblate
        global selection
        selection = 'oblate'
        self.Destroy()
        event.Skip()

    def ellipsoid(self, event): # ellipsoid
        global selection
        selection = 'ellipsoid'
        self.Destroy()
        event.Skip()

    def final(self, event): # final
        global selection
        selection = 'final'
        self.Destroy()
        event.Skip()

    def cancel(self, event): # cancel
        global selection
        selection = None
        self.Destroy()
        event.Skip()

# end of class select_tensor

def check_entries(self):
    check = False
    counter = 0

    # check frq 1
    if not self.modelfreefreq1.GetValue() == '':
         counter = counter + 1
    if not self.m_noe_1.GetValue() == '':
         counter = counter + 1
    if not self.m_r1_1.GetValue() == '':
         counter = counter + 1
    if not self.m_r2_1.GetValue() == '':
         counter = counter + 1

    # check frq 1
    if not self.modelfreefreq2.GetValue() == '':
         counter = counter + 1
    if not self.m_noe_2.GetValue() == '':
         counter = counter + 1
    if not self.m_r1_2.GetValue() == '':
         counter = counter + 1
    if not self.m_r2_2.GetValue() == '':
         counter = counter + 1

    # check frq 1
    if not self.modelfreefreq3.GetValue() == '':
         counter = counter + 1
    if not self.m_noe_3.GetValue() == '':
         counter = counter + 1
    if not self.m_r1_3.GetValue() == '':
         counter = counter + 1
    if not self.m_r2_3.GetValue() == '':
         counter = counter + 1

    # two field strength ok
    if counter == 8:
      check = True
      print '\n\n\nTwo different field strength detected !!\n\n\n'


    # three field strength ok
    elif counter == 12:
      check = True
      print '\n\n\nThree different field strength detected !!\n\n\n'


    # missing data
    else:
      missing_data()       

    return check


def whichmodel():
    global selection
    selection = None
    dlg = select_tensor(None, -1, "")
    dlg.ShowModal()
    return selection


