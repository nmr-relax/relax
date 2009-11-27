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
from wxPython.wx import wxFrame
import wx


class Settings(wxFrame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: Settings.__init__
        kwds["style"] = wxDEFAULT_FRAME_STYLE|wx.STAY_ON_TOP
        wxFrame.__init__(self, *args, **kwds)
        self.panel_1 = wxPanel(self, -1)
        self.title = wxStaticText(self, -1, "relaxGUI Global Settings", style=wxALIGN_CENTRE)
        self.label_1 = wxStaticText(self, -1, "Global Settings:")
        self.label_2 = wxStaticText(self, -1, "Bond length:")
        self.bond = wxTextCtrl(self, -1, "1.02 * 1e-10")
        self.label_3 = wxStaticText(self, -1, "CSA:")
        self.csa = wxTextCtrl(self, -1, "-172 * 1e-6")
        self.label_4 = wxStaticText(self, -1, "Grid search increase:")
        self.grid_inc = wxTextCtrl(self, -1, "11")
        self.label_5 = wxStaticText(self, -1, "Number of Monte Carlo\nSimulations:")
        self.mc_no = wxTextCtrl(self, -1, "500")
        self.label_6 = wxStaticText(self, -1, "Minimisation algorithm:")
        self.minimisation = wxTextCtrl(self, -1, "")
        self.label_7 = wxStaticText(self, -1, "Peak Lists (colons):")
        self.label_8 = wxStaticText(self, -1, "Residue number:")
        self.res_col = wxTextCtrl(self, -1, "")
        self.label_9 = wxStaticText(self, -1, "Intensities:")
        self.int_col = wxTextCtrl(self, -1, "")
        self.label_10 = wxStaticText(self, -1, "Error:")
        self.err_col = wxTextCtrl(self, -1, "")
        self.label_11 = wxStaticText(self, -1, "")
        self.save_button = wxButton(self.panel_1, -1, "Save")
        self.cancel_button = wxButton(self.panel_1, -1, "Cancel")

        self.__set_properties()
        self.__do_layout()

        EVT_BUTTON(self, self.save_button.GetId(), self.save)
        EVT_BUTTON(self, self.cancel_button.GetId(), self.cancel)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: Settings.__set_properties
        self.SetTitle("Settings")
        _icon = wxEmptyIcon()
        _icon.CopyFromBitmap(wxBitmap(sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax_start.gif', wxBITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.title.SetFont(wxFont(15, wxDEFAULT, wxITALIC, wxNORMAL, 0, ""))
        self.label_1.SetMinSize((155, 17))
        self.label_1.SetFont(wxFont(10, wxDEFAULT, wxNORMAL, wxBOLD, 0, ""))
        self.label_2.SetMinSize((155, 17))
        self.bond.SetMinSize((100, 27))
        self.label_3.SetMinSize((155, 17))
        self.csa.SetMinSize((100, 27))
        self.label_4.SetMinSize((155, 17))
        self.grid_inc.SetMinSize((100, 27))
        self.label_5.SetMinSize((155, 34))
        self.mc_no.SetMinSize((100, 27))
        self.label_6.SetMinSize((155, 17))
        self.minimisation.SetMinSize((100, 27))
        self.label_7.SetMinSize((155, 17))
        self.label_7.SetFont(wxFont(10, wxDEFAULT, wxNORMAL, wxBOLD, 0, ""))
        self.label_8.SetMinSize((155, 17))
        self.res_col.SetMinSize((100, 27))
        self.label_9.SetMinSize((155, 17))
        self.int_col.SetMinSize((100, 27))
        self.label_10.SetMinSize((155, 17))
        self.err_col.SetMinSize((100, 27))
        self.save_button.SetMinSize((103, 27))
        self.cancel_button.SetMinSize((103, 27))
        self.panel_1.SetMinSize((251, 5))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: Settings.__do_layout
        sizer_2 = wxBoxSizer(wxVERTICAL)
        sizer_3 = wxBoxSizer(wxHORIZONTAL)
        sizer_5 = wxBoxSizer(wxVERTICAL)
        sizer_16 = wxBoxSizer(wxHORIZONTAL)
        sizer_15 = wxBoxSizer(wxHORIZONTAL)
        sizer_14 = wxBoxSizer(wxHORIZONTAL)
        sizer_13 = wxBoxSizer(wxHORIZONTAL)
        sizer_12 = wxBoxSizer(wxHORIZONTAL)
        sizer_11 = wxBoxSizer(wxHORIZONTAL)
        sizer_10 = wxBoxSizer(wxHORIZONTAL)
        sizer_9 = wxBoxSizer(wxHORIZONTAL)
        sizer_8 = wxBoxSizer(wxHORIZONTAL)
        sizer_7 = wxBoxSizer(wxHORIZONTAL)
        sizer_6 = wxBoxSizer(wxHORIZONTAL)
        sizer_2.Add(self.title, 0, wxALL|wxADJUST_MINSIZE, 10)
        sizer_6.Add(self.label_1, 0, wxTOP|wxADJUST_MINSIZE, 2)
        sizer_5.Add(sizer_6, 1, wxEXPAND, 0)
        sizer_7.Add(self.label_2, 0, wxTOP|wxBOTTOM|wxADJUST_MINSIZE, 3)
        sizer_7.Add(self.bond, 0, wxADJUST_MINSIZE, 0)
        sizer_5.Add(sizer_7, 1, wxEXPAND, 0)
        sizer_8.Add(self.label_3, 0, wxTOP|wxBOTTOM|wxADJUST_MINSIZE, 3)
        sizer_8.Add(self.csa, 0, wxADJUST_MINSIZE, 0)
        sizer_5.Add(sizer_8, 1, wxEXPAND, 0)
        sizer_9.Add(self.label_4, 0, wxTOP|wxBOTTOM|wxADJUST_MINSIZE, 3)
        sizer_9.Add(self.grid_inc, 0, wxADJUST_MINSIZE, 0)
        sizer_5.Add(sizer_9, 1, wxEXPAND, 0)
        sizer_10.Add(self.label_5, 0, wxTOP|wxBOTTOM|wxADJUST_MINSIZE, 3)
        sizer_10.Add(self.mc_no, 0, wxADJUST_MINSIZE, 0)
        sizer_5.Add(sizer_10, 1, wxEXPAND, 0)
        sizer_11.Add(self.label_6, 0, wxTOP|wxBOTTOM|wxADJUST_MINSIZE, 3)
        sizer_11.Add(self.minimisation, 0, wxADJUST_MINSIZE, 0)
        sizer_5.Add(sizer_11, 1, wxEXPAND, 0)
        sizer_12.Add(self.label_7, 0, wxTOP|wxADJUST_MINSIZE, 6)
        sizer_5.Add(sizer_12, 1, wxEXPAND, 0)
        sizer_13.Add(self.label_8, 0, wxTOP|wxBOTTOM|wxADJUST_MINSIZE, 3)
        sizer_13.Add(self.res_col, 0, wxADJUST_MINSIZE, 0)
        sizer_5.Add(sizer_13, 1, wxEXPAND, 0)
        sizer_14.Add(self.label_9, 0, wxTOP|wxBOTTOM|wxADJUST_MINSIZE, 3)
        sizer_14.Add(self.int_col, 0, wxADJUST_MINSIZE, 0)
        sizer_5.Add(sizer_14, 1, wxEXPAND, 0)
        sizer_15.Add(self.label_10, 0, wxTOP|wxBOTTOM|wxADJUST_MINSIZE, 3)
        sizer_15.Add(self.err_col, 0, wxADJUST_MINSIZE, 0)
        sizer_5.Add(sizer_15, 1, wxEXPAND, 0)
        sizer_5.Add(self.label_11, 0, wxADJUST_MINSIZE, 0)
        sizer_16.Add(self.save_button, 0, wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL|wxADJUST_MINSIZE, 0)
        sizer_16.Add(self.cancel_button, 0, wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL|wxADJUST_MINSIZE, 0)
        self.panel_1.SetSizer(sizer_16)
        sizer_5.Add(self.panel_1, 1, wxEXPAND, 0)
        sizer_3.Add(sizer_5, 1, wxLEFT|wxSHAPED, 5)
        sizer_2.Add(sizer_3, 1, wxEXPAND, 0)
        self.SetSizer(sizer_2)
        sizer_2.Fit(self)
        self.Layout()
        self.Centre()
        # end wxGlade

    def save(self, event): 
        print "Save settings not yet implemented!"
        self.Close()
        event.Skip()

    def cancel(self, event): 
        self.Close()
        event.Skip()

# end of class Settings


def relax_settings():
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    start = Settings(None, -1, "")
    app.SetTopWindow(start)
    start.Show()
    app.MainLoop()
