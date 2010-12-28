
import wx

from gui_bieri.analyses.auto_model_free import About_window

app = wx.App(0)
win = About_window(None)
win.Show()
app.MainLoop()
