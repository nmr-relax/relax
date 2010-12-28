
import wx

from gui_bieri.about import About_relax

app = wx.App(0)
win = About_relax(None)
win.Show()
app.MainLoop()
