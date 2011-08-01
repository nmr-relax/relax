###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
import sys
import wx

# relax module imports.
from generic_fns.pipes import cdp_name
from status import Status; status = Status()

# relax GUI module imports.
from gui.fonts import font
from gui.icons import relax_icons
from gui.misc import add_border, str_to_gui
from gui.paths import IMAGE_PATH


class Controller(wx.Frame):
    """The relax controller window."""

    def __init__(self, gui):
        """Set up the relax controller frame.

        @param gui:     The GUI object.
        @type gui:      wx.Frame instance
        """

        # Store the args.
        self.gui = gui

        # Initialise the base class.
        super(Controller, self).__init__(self.gui, -1, style=wx.DEFAULT_FRAME_STYLE|wx.STAY_ON_TOP)

        # Some default values.
        self.size_x = 800
        self.size_y = 700
        self.border = 5
        self.spacer = 10

        # Set up the frame.
        sizer = self.setup_frame()

        # Add the relax logo.
        self.add_relax_logo(sizer)

        # Spacing.
        sizer.AddSpacer(20)

        # Add the current analysis info.
        self.name = self.add_text(self, sizer, "Current GUI analysis:")

        # Add the current data pipe info.
        self.cdp = self.add_text(self, sizer, "Current data pipe:")

        # Create the model-free specific panel.
        self.create_mf(sizer)

        # Add the main execution gauge.
        self.main_gauge = self.add_gauge(self, sizer, "Execution status:")

        # Add the log panel.
        self.add_log(sizer)

        # IO redirection.
        if not status.debug and not status.test_mode:
            redir = Redirect_text(self.log_panel)
            sys.stdout = redir
            sys.stderr = redir

        # Initial update of the controller.
        self.update_controller()

        # Register functions with the observer objects.
        status.observers.pipe_alteration.register('controller', self.update_controller)
        status.observers.auto_analyses.register('controller', self.update_controller)
        status.observers.gui_analysis.register('controller', self.update_controller)
        status.observers.exec_lock.register('controller', self.update_gauge)


    def add_gauge(self, parent, sizer, desc):
        """Add a gauge to the sizer and return it.

        @param parent:  The parent GUI element.
        @type parent:   wx object
        @param sizer:   The sizer element to pack the element into.
        @type sizer:    wx.Sizer instance
        @param desc:    The description to display.
        @type desc:     str
        @return:        The gauge element.
        @rtype:         wx.Gauge instance
        """

        # Create a horizontal layout.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The intro.
        text = wx.StaticText(parent, -1, desc, style=wx.ALIGN_LEFT)
        text.SetFont(font.normal)
        sub_sizer.Add(text, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        # The gauge.
        gauge = wx.Gauge(parent, id=-1, range=100, style=wx.GA_SMOOTH)
        gauge.SetSize((-1, 20))
        sub_sizer.Add(gauge, 3, wx.EXPAND|wx.ALL, 0)

        # Add the sizer.
        sizer.Add(sub_sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Spacing.
        sizer.AddSpacer(self.spacer)

        # Return the gauge.
        return gauge


    def add_log(self, sizer):
        """Add the log panel to the sizer.

        @param sizer:   The sizer element to pack the log panel into.
        @type sizer:    wx.Sizer instance
        """

        # Log panel (TE_RICH2 is to prevent problems on MS Windows).
        self.log_panel = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)

        # Set the font info.
        self.log_panel.SetFont(font.normal)

        # Add to the sizer.
        sizer.Add(self.log_panel, 1, wx.EXPAND|wx.ALL, 0)


    def add_relax_logo(self, sizer):
        """Add the relax logo to the sizer.

        @param sizer:   The sizer element to pack the relax logo into.
        @type sizer:    wx.Sizer instance
        """

        # The logo.
        logo = wx.StaticBitmap(self, -1, wx.Bitmap(IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))

        # Add the relax logo.
        sizer.Add(logo, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Spacing.
        sizer.AddSpacer(self.spacer)


    def add_text(self, parent, sizer, desc):
        """Add the current data pipe element.

        @param parent:  The parent GUI element.
        @type parent:   wx object
        @param sizer:   The sizer element to pack the element into.
        @type sizer:    wx.Sizer instance
        @param desc:    The description to display.
        @type desc:     str
        @return:        The text control.
        @rtype:         wx.TextCtrl instance
        """

        # Create a horizontal layout.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The intro.
        text = wx.StaticText(parent, -1, desc, style=wx.ALIGN_LEFT)
        text.SetFont(font.normal)
        sub_sizer.Add(text, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        # The cdp name.
        field = wx.TextCtrl(parent, -1, '', style=wx.ALIGN_LEFT)
        field.SetEditable(False)
        field.SetFont(font.normal)
        colour = self.GetBackgroundColour()
        field.SetOwnBackgroundColour(colour)
        sub_sizer.Add(field, 3, wx.ALIGN_CENTER_VERTICAL, 0)

        # Add the sizer.
        sizer.Add(sub_sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Spacing.
        sizer.AddSpacer(self.spacer)

        # Return the control.
        return field


    def analysis_key(self):
        """Return the key for the current analysis' status object.

        @return:    The current analysis' status object key.
        @rtype:     str or None
        """

        # Get the data container.
        data = self.gui.analysis.current_data()
        if data == None:
            return

        # Return the pipe name, if it exists, as the key.
        if hasattr(data, 'pipe_name'):
            return data.pipe_name


    def create_mf(self, sizer):
        """Create the model-free specific panel.

        @param sizer:   The sizer element to pack the element into.
        @type sizer:    wx.Sizer instance
        """

        # Create a panel.
        self.panel_mf = wx.Panel(self, -1)
        sizer.Add(self.panel_mf, 0, wx.ALL|wx.EXPAND, 0)

        # The panel sizer.
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel_mf.SetSizer(panel_sizer)

        # Add the global model.
        self.global_model = self.add_text(self.panel_mf, panel_sizer, "Global model:")

        # Progress gauge.
        self.progress_gauge = self.add_gauge(self.panel_mf, panel_sizer, "Incremental progress:")

        # MC sim gauge.
        self.mc_gauge = self.add_gauge(self.panel_mf, panel_sizer, "Monte Carlo simulations:")


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close the window.
        self.Hide()


    def setup_frame(self):
        """Set up the relax controller frame.
        @return:    The sizer object.
        @rtype:     wx.Sizer instance
        """

        # Set the frame title.
        self.SetTitle("The relax controller")

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # Use a grid sizer for packing the elements.
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Pack the sizer into the frame.
        self.SetSizer(main_sizer)

        # Build the central sizer, with borders.
        sizer = add_border(main_sizer, border=self.border, packing=wx.VERTICAL)

        # Close the window cleanly (hide so it can be reopened).
        self.Bind(wx.EVT_CLOSE, self.handler_close)

        # Set the default size of the controller.
        self.SetSize((self.size_x, self.size_y))

        # Centre the frame.
        self.Centre()

        # Return the central sizer.
        return sizer


    def update_controller(self):
        """Update the relax controller."""

        # First freeze the controller.
        self.Freeze()

        # Set the current data pipe info.
        pipe = cdp_name()
        if pipe == None:
            pipe = ''
        self.cdp.SetValue(str_to_gui(pipe))

        # Set the current GUI analysis info.
        name = self.gui.analysis.current_analysis_name()
        if name == None:
            name = ''
        self.name.SetValue(str_to_gui(name))

        # The analysis type.
        type = self.gui.analysis.current_analysis_type()

        # Model-free auto-analysis.
        if type == 'model-free':
            self.panel_mf.Show()
            self.update_mf()
        else:
            self.panel_mf.Hide()

        # Update the main gauge.
        self.update_gauge()

        # Re-perform a layout.
        self.Layout()
        self.Refresh()

        # Finally thaw the controller.
        self.Thaw()


    def update_gauge(self):
        """Update the main execution gauge."""

        # Pulse during execution.
        if status.exec_lock.locked():
            self.main_gauge.Pulse()

        # Finished.
        key = self.analysis_key()
        if key and status.auto_analysis.has_key(key) and status.auto_analysis[key].fin:
            self.main_gauge.SetValue(100)

        # Reset the gauge.
        if not status.exec_lock.locked():
            # No key, so reset.
            if not key or not status.auto_analysis.has_key(key):
                self.main_gauge.SetValue(0)

            # Key present, but analysis not started.
            if key and status.auto_analysis.has_key(key) and not status.auto_analysis[key].fin:
                self.main_gauge.SetValue(0)


    def update_mf(self):
        """Update the model-free specific elements."""

        # The analysis key.
        key = self.analysis_key()
        if not key or not status.auto_analysis.has_key(key):
            return

        # Set the diffusion model.
        self.global_model.SetValue(status.auto_analysis[key].diff_model)

        # Update the progress gauge for the local tm model.
        if status.auto_analysis[key].diff_model == 'local_tm':
            if status.auto_analysis[key].current_model:
                # Current model.
                no = int(status.auto_analysis[key].current_model[2:])

                # Total selected models.
                total_models = len(status.auto_analysis[key].local_tm_models)

                # Update the progress bar.
                percent = int(100 * no / float(total_models))
                if percent > 100:
                    percent = 100
                wx.CallAfter(self.progress_gauge.SetValue, percent)

        # Sphere to Ellipsoid Models.
        elif status.auto_analysis[key].diff_model in ['sphere', 'prolate', 'oblate', 'ellipsoid']:
            # The round as a percentage.
            percent = int(100 * (status.auto_analysis[key].round - 1) / status.auto_analysis[key].max_iter)
            if percent > 100:
                percent = 100

            # Update the progress bar.
            wx.CallAfter(self.progress_gauge.SetValue, percent)

        # Monte Carlo simulations.
        if status.auto_analysis[key].mc_number:
            # The simulation number as a percentage.
            percent = int(100 * (status.auto_analysis[key].mc_number + 2) / cdp.sim_number)
            if percent > 100:
                percent = 100

            # Update the progress bar.
            wx.CallAfter(self.mc_gauge.SetValue, percent)




class Redirect_text(object):
    """The IO redirection to text control object."""

    def __init__(self, control, max_entries=100000):
        """Set up the text redirection object.

        @param control:         The text control object to redirect IO to.
        @type control:          wx.TextCtrl instance
        @keyword max_entries:   Limit the scroll back to this many lines.
        @type max_entries:      int
        """

        # Store the args.
        self.control = control
        self.max_entries = max_entries


    def append_text(self, string):
        """Update the text control.

        @param string:  The text to write.
        @type string:   str
        """

        # Limit scroll back by removing lines.
        if self.control.GetNumberOfLines() > self.max_entries:
            self.control.Remove(0, self.control.GetLineLength(0) + 1)
            self.control.Refresh()

        # Append the text to the controller asynchronously.
        self.control.AppendText(string)


    def write(self, string):
        """Simulate the file object write method.

        @param string:  The text to write.
        @type string:   str
        """

        # Append the text to the controller asynchronously, with limited scroll back.
        wx.CallAfter(self.append_text, string)
