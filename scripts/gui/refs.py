
import wx

from gui_bieri.references import References

app = wx.App(0)
ref = References(None)
ref.Show()
app.MainLoop()
