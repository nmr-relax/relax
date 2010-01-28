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

# Python module imports.
from os import sep
import wx

# relax GUI module imports.
from gui_bieri.paths import IMAGE_PATH


class Select_tensor(wx.Dialog):
    def __init__(self, *args, **kwds):
        """Initialise the dialog."""

        # Strip out and save the local_tm_flag from the keywords.
        self.local_tm_flag = kwds.pop('local_tm_flag')

        # The selection string.
        self.selection = None

        # begin select_tensor.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_13 = wx.StaticText(self, -1, "Select Calculation Mode:")
        self.label_2_copy_copy_copy = wx.StaticText(self, -1, "Automatic")
        self.button_4_copy_copy = wx.Button(self, -1, "Full Analysis")
        self.label_7_copy_copy_copy = wx.StaticText(self, -1, "Local tm")
        self.local_tm_button = wx.Button(self, -1, "Local tm")
        self.label_8_copy_copy = wx.StaticText(self, -1, "Sphere")
        self.sphere_button = wx.BitmapButton(self, -1, wx.Bitmap(IMAGE_PATH+'sphere.jpg', wx.BITMAP_TYPE_ANY))
        self.label_9_copy_copy_copy = wx.StaticText(self, -1, "Prolate")
        self.oblate_button = wx.BitmapButton(self, -1, wx.Bitmap(IMAGE_PATH+'prolate.jpg', wx.BITMAP_TYPE_ANY))
        self.label_10_copy_copy_copy = wx.StaticText(self, -1, "Oblate")
        self.prolate_button = wx.BitmapButton(self, -1, wx.Bitmap(IMAGE_PATH+'oblate.jpg', wx.BITMAP_TYPE_ANY))
        self.label_11_copy_copy_copy = wx.StaticText(self, -1, "Ellipsoid")
        self.ellipsoid_button = wx.BitmapButton(self, -1, wx.Bitmap(IMAGE_PATH+'ellipsoid.jpg', wx.BITMAP_TYPE_ANY))
        self.label_12_copy_copy_copy = wx.StaticText(self, -1, "Final")
        self.final_button = wx.Button(self, -1, "Final")
        self.panel_2_copy = wx.Panel(self, -1)
        self.cancel_button = wx.Button(self, -1, "Cancel")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.full, self.button_4_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.sphere, self.sphere_button)
        self.Bind(wx.EVT_BUTTON, self.prolate, self.oblate_button)
        self.Bind(wx.EVT_BUTTON, self.oblate, self.prolate_button)
        self.Bind(wx.EVT_BUTTON, self.ellipsoid, self.ellipsoid_button)
        self.Bind(wx.EVT_BUTTON, self.final, self.final_button)
        self.Bind(wx.EVT_BUTTON, self.cancel, self.cancel_button)
        self.Bind(wx.EVT_BUTTON, self.local, self.local_tm_button)


    def __do_layout(self):
        # begin select_tensor.__do_layout
        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1_copy = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_9.Add(self.label_13, 0, wx.ALL, 5)
        grid_sizer_1_copy.Add(self.label_2_copy_copy_copy, 0, wx.LEFT|wx.TOP|wx.SHAPED, 5)
        grid_sizer_1_copy.Add(self.button_4_copy_copy, 0, 0, 0)
        grid_sizer_1_copy.Add(self.label_7_copy_copy_copy, 0, wx.LEFT|wx.EXPAND, 5)
        grid_sizer_1_copy.Add(self.local_tm_button, 0, wx.SHAPED, 0)
        grid_sizer_1_copy.Add(self.label_8_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.sphere_button, 0, wx.SHAPED, 0)
        grid_sizer_1_copy.Add(self.label_9_copy_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.oblate_button, 0, wx.SHAPED, 0)
        grid_sizer_1_copy.Add(self.label_10_copy_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.prolate_button, 0, wx.SHAPED, 0)
        grid_sizer_1_copy.Add(self.label_11_copy_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.ellipsoid_button, 0, 0, 0)
        grid_sizer_1_copy.Add(self.label_12_copy_copy_copy, 0, wx.LEFT|wx.SHAPED, 5)
        grid_sizer_1_copy.Add(self.final_button, 0, 0, 0)
        grid_sizer_1_copy.Add(self.panel_2_copy, 1, wx.EXPAND, 0)
        grid_sizer_1_copy.Add(self.cancel_button, 0, 0, 0)
        sizer_9.Add(grid_sizer_1_copy, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_9)
        sizer_9.Fit(self)
        self.Layout()


    def __set_properties(self):
        # begin  select_tensor.__set_properties
        self.SetTitle("relaxGUI")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.label_13.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_2_copy_copy_copy.SetMinSize((100, 29))
        self.button_4_copy_copy.SetMinSize((111, 29))
        self.label_7_copy_copy_copy.SetMinSize((100, 17))
        self.local_tm_button.SetMinSize((111, 29))
        self.label_8_copy_copy.SetMinSize((100, 17))
        self.sphere_button.SetSize(self.sphere_button.GetBestSize())
        self.label_9_copy_copy_copy.SetMinSize((100, 17))
        self.oblate_button.SetSize(self.oblate_button.GetBestSize())
        self.label_10_copy_copy_copy.SetMinSize((100, 17))
        self.prolate_button.SetSize(self.prolate_button.GetBestSize())
        self.label_11_copy_copy_copy.SetMinSize((100, 17))
        self.ellipsoid_button.SetSize(self.ellipsoid_button.GetBestSize())
        self.label_12_copy_copy_copy.SetMinSize((100, 28))
        self.final_button.SetMinSize((111, 29))
        self.panel_2_copy.SetMinSize((100, 29))
        self.cancel_button.SetMinSize((111, 29))

        # enable or disable buttons if local_tm was calculate
        self.sphere_button.Enable(self.local_tm_flag) # sphere button
        self.oblate_button.Enable(self.local_tm_flag)  # prolate button
        self.prolate_button.Enable(self.local_tm_flag)  # oblate button
        self.ellipsoid_button.Enable(self.local_tm_flag)  # ellipsoid button
        self.final_button.Enable(self.local_tm_flag)  # final button


    def cancel(self, event): # cancel
        self.selection = None
        self.Destroy()
        event.Skip()


    def ellipsoid(self, event): # ellipsoid
        self.selection = 'ellipsoid'
        self.Destroy()
        event.Skip()


    def final(self, event): # final
        self.selection = 'final'
        self.Destroy()
        event.Skip()


    def full(self, event): # automatic
        self.selection = 'full'
        self.Close()
        event.Skip()


    def local(self, event): # local tm
        self.selection = 'local_tm'
        self.Destroy()
        event.Skip()


    def oblate(self, event): # oblate
        self.selection = 'oblate'
        self.Destroy()
        event.Skip()


    def prolate(self, event): # prolate
        self.selection = 'prolate'
        self.Destroy()
        event.Skip()


    def sphere(self, event): # sphere
        self.selection = 'sphere'
        self.Close()
        event.Skip()
