
import wx

from gui_bieri.about import About_gui

app = wx.App(0)
win = About_gui(None)
win.Show()
app.MainLoop()
