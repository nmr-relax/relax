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
import sys
import wx

# relax GUI module imports.
from filedialog import openfile
from paths import IMAGE_PATH


def relax_global_settings(oldsettings):
    global settings
    global old_settings
    settings = []
    old_settings = oldsettings
    set_relax_params = Globalparam(None, -1, "")
    set_relax_params.ShowModal()
    return settings


def import_file_settings(oldsettings):
    global settings
    global old_settings
    settings = []
    old_settings = oldsettings
    set_relax_params = Inputfile(None, -1, "")
    set_relax_params.ShowModal()
    return settings


def load_sequence(self):
    seqfile = openfile('Choose Sequence File', sys.path[-1], '', 'all files (*.*)|*.*')
    return seqfile



class Globalparam(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin globalparam.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_1_copy = wx.StaticText(self, -1, "Global Parameters for relax")
        self.bitmap_1_copy = wx.StaticBitmap(self, -1, wx.Bitmap(IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))
        self.label_2_copy = wx.StaticText(self, -1, "Bond Length-:")
        self.bond = wx.TextCtrl(self, -1, old_settings[0])
        self.label_3_copy = wx.StaticText(self, -1, "CSA")
        self.csa = wx.TextCtrl(self, -1, old_settings[1])
        self.label_5_copy = wx.StaticText(self, -1, "Hetero Nucleus")
        self.hetero = wx.TextCtrl(self, -1, old_settings[2])
        self.label_6_copy = wx.StaticText(self, -1, "Proton")
        self.prot = wx.TextCtrl(self, -1, old_settings[3])
        self.label_9_copy = wx.StaticText(self, -1, "Grid Search Increase")
        self.grid = wx.TextCtrl(self, -1, old_settings[4])
        self.label_7_copy = wx.StaticText(self, -1, "Minimisation Algrithm")
        self.minim = wx.TextCtrl(self, -1, old_settings[5])
        self.label_8_copy = wx.StaticText(self, -1, "Monte Carlo Simulations")
        self.monte = wx.TextCtrl(self, -1, old_settings[6])
        self.ok_copy = wx.Button(self, -1, "Ok")
        self.cancel_copy = wx.Button(self, -1, "Cancel")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.accept_settings, self.ok_copy)
        self.Bind(wx.EVT_BUTTON, self.cancel_settings, self.cancel_copy)


    def __do_layout(self):
        # begin  globalparam.__do_layout
        sizer_1_copy = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1_copy = wx.GridSizer(8, 2, 0, 0)
        sizer_1_copy.Add(self.label_1_copy, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_1_copy.Add(self.bitmap_1_copy, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        grid_sizer_1_copy.Add(self.label_2_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.bond, 0, 0, 0)
        grid_sizer_1_copy.Add(self.label_3_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.csa, 0, 0, 0)
        grid_sizer_1_copy.Add(self.label_5_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.hetero, 0, 0, 0)
        grid_sizer_1_copy.Add(self.label_6_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.prot, 0, 0, 0)
        grid_sizer_1_copy.Add(self.label_9_copy, 0, 0, 0)
        grid_sizer_1_copy.Add(self.grid, 0, 0, 0)
        grid_sizer_1_copy.Add(self.label_7_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.minim, 0, 0, 0)
        grid_sizer_1_copy.Add(self.label_8_copy, 0, wx.LEFT|wx.RIGHT, 5)
        grid_sizer_1_copy.Add(self.monte, 0, 0, 0)
        grid_sizer_1_copy.Add(self.ok_copy, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        grid_sizer_1_copy.Add(self.cancel_copy, 0, wx.ALL, 5)
        sizer_1_copy.Add(grid_sizer_1_copy, 1, wx.SHAPED, 0)
        self.SetSizer(sizer_1_copy)
        sizer_1_copy.Fit(self)
        self.Layout()


    def __set_properties(self):
        # begin globalparam.__set_properties
        self.SetTitle("relaxGUI")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.label_1_copy.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bond.SetMinSize((150, 27))
        self.csa.SetMinSize((150, 27))
        self.hetero.SetMinSize((150, 27))
        self.prot.SetMinSize((150, 27))
        self.grid.SetMinSize((150, 27))
        self.minim.SetMinSize((150, 27))
        self.label_8_copy.SetMinSize((156, 17))
        self.monte.SetMinSize((150, 27))


    def accept_settings(self, event): # change settings
        global settings
        settings = []
        settings.append(str(self.bond.GetValue()))
        settings.append(str(self.csa.GetValue()))
        settings.append(str(self.hetero.GetValue()))
        settings.append(str(self.prot.GetValue()))
        settings.append(str(self.grid.GetValue()))
        settings.append(str(self.minim.GetValue()))
        settings.append(str(self.monte.GetValue()))
        self.Destroy()
        event.Skip()


    def cancel_settings(self, event): # do not change settings
        global settings
        settings = None
        self.Destroy()
        event.Skip()



class Inputfile(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin inputfile.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_1_copy_copy = wx.StaticText(self, -1, "Parameter File Settings")
        self.bitmap_1_copy_copy = wx.StaticBitmap(self, -1, wx.Bitmap(IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))
        self.subheader = wx.StaticText(self, -1, "Please specify culumn number below:\n")
        self.label_2_copy_copy = wx.StaticText(self, -1, "Molecule Name")
        self.mol_nam = wx.TextCtrl(self, -1, old_settings[0])
        self.label_3_copy_copy = wx.StaticText(self, -1, "Residue Number")
        self.res_num_col = wx.TextCtrl(self, -1, old_settings[1])
        self.label_5_copy_copy = wx.StaticText(self, -1, "Residue Name")
        self.res_nam_col = wx.TextCtrl(self, -1, old_settings[2])
        self.label_6_copy_copy = wx.StaticText(self, -1, "Spin Number")
        self.spin_num_col = wx.TextCtrl(self, -1, old_settings[3])
        self.label_9_copy_copy = wx.StaticText(self, -1, "Spin Name")
        self.spin_nam_col = wx.TextCtrl(self, -1, old_settings[4])
        self.label_7_copy_copy = wx.StaticText(self, -1, "Values")
        self.value_col = wx.TextCtrl(self, -1, old_settings[5])
        self.label_8_copy_copy = wx.StaticText(self, -1, "Errors")
        self.error_col = wx.TextCtrl(self, -1, old_settings[6])
        self.ok_copy_copy = wx.Button(self, -1, "Ok")
        self.cancel_copy_copy = wx.Button(self, -1, "Cancel")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.accept_settings, self.ok_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.cancel_settings, self.cancel_copy_copy)


    def __do_layout(self):
        # begin inputfile.__do_layout
        sizer_1_copy_copy = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1_copy_copy = wx.GridSizer(8, 2, 0, 0)
        sizer_1_copy_copy.Add(self.label_1_copy_copy, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_1_copy_copy.Add(self.bitmap_1_copy_copy, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_1_copy_copy.Add(self.subheader, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        grid_sizer_1_copy_copy.Add(self.label_2_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy_copy.Add(self.mol_nam, 0, 0, 0)
        grid_sizer_1_copy_copy.Add(self.label_3_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy_copy.Add(self.res_num_col, 0, 0, 0)
        grid_sizer_1_copy_copy.Add(self.label_5_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy_copy.Add(self.res_nam_col, 0, 0, 0)
        grid_sizer_1_copy_copy.Add(self.label_6_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy_copy.Add(self.spin_num_col, 0, 0, 0)
        grid_sizer_1_copy_copy.Add(self.label_9_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy_copy.Add(self.spin_nam_col, 0, 0, 0)
        grid_sizer_1_copy_copy.Add(self.label_7_copy_copy, 0, wx.LEFT, 5)
        grid_sizer_1_copy_copy.Add(self.value_col, 0, 0, 0)
        grid_sizer_1_copy_copy.Add(self.label_8_copy_copy, 0, wx.LEFT|wx.RIGHT, 5)
        grid_sizer_1_copy_copy.Add(self.error_col, 0, 0, 0)
        grid_sizer_1_copy_copy.Add(self.ok_copy_copy, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        grid_sizer_1_copy_copy.Add(self.cancel_copy_copy, 0, wx.ALL, 5)
        sizer_1_copy_copy.Add(grid_sizer_1_copy_copy, 1, wx.SHAPED, 0)
        self.SetSizer(sizer_1_copy_copy)
        sizer_1_copy_copy.Fit(self)
        self.Layout()


    def __set_properties(self):
        # begin inputfile.__set_properties
        self.SetTitle("relaxGUI")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.label_1_copy_copy.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.mol_nam.SetMinSize((150, 27))
        self.res_num_col.SetMinSize((150, 27))
        self.res_nam_col.SetMinSize((150, 27))
        self.spin_num_col.SetMinSize((150, 27))
        self.spin_nam_col.SetMinSize((150, 27))
        self.value_col.SetMinSize((150, 27))
        self.label_8_copy_copy.SetMinSize((156, 17))
        self.error_col.SetMinSize((150, 27))


    def accept_settings(self, event): # change settings
        global settings
        settings = []
        settings.append(str(self.mol_nam.GetValue()))
        settings.append(str(self.res_num_col.GetValue()))
        settings.append(str(self.res_nam_col.GetValue()))
        settings.append(str(self.spin_num_col.GetValue()))
        settings.append(str(self.spin_nam_col.GetValue()))
        settings.append(str(self.value_col.GetValue()))
        settings.append(str(self.error_col.GetValue()))
        self.Destroy()
        event.Skip()


    def cancel_settings(self, event): # cancel
        global settings
        settings = None
        self.Destroy()
        event.Skip()
