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
from Queue import Queue
import sys
import wx
import wx.stc

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
        super(Controller, self).__init__(self.gui, -1, style=wx.DEFAULT_FRAME_STYLE)

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

        # Create the relaxation curve-fitting specific panel.
        self.create_rx(sizer)

        # Create the model-free specific panel.
        self.create_mf(sizer)

        # Add the main execution gauge.
        self.main_gauge = self.add_gauge(self, sizer, "Execution status:")

        # Initialise a queue for log messages.
        self.log_queue = Queue()

        # Add the log panel.
        self.log_panel = LogCtrl(self, log_queue=self.log_queue, id=-1)
        sizer.Add(self.log_panel, 1, wx.EXPAND|wx.ALL, 0)

        # IO redirection.
        sys.stdout = Redirect_text(self.log_panel, self.log_queue, stream=0)
        sys.stderr = Redirect_text(self.log_panel, self.log_queue, stream=1)

        # Initial update of the controller.
        self.update_controller()

        # Create a timer for updating the gauges.
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.handler_timer, self.timer)

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
        self.global_model_mf = self.add_text(self.panel_mf, panel_sizer, "Global model:")

        # Progress gauge.
        self.progress_gauge_mf = self.add_gauge(self.panel_mf, panel_sizer, "Incremental progress:")

        # MC sim gauge.
        self.mc_gauge_mf = self.add_gauge(self.panel_mf, panel_sizer, "Monte Carlo simulations:")


    def create_rx(self, sizer):
        """Create the relaxation curve-fitting specific panel.

        @param sizer:   The sizer element to pack the element into.
        @type sizer:    wx.Sizer instance
        """

        # Create a panel.
        self.panel_rx = wx.Panel(self, -1)
        sizer.Add(self.panel_rx, 0, wx.ALL|wx.EXPAND, 0)

        # The panel sizer.
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel_rx.SetSizer(panel_sizer)

        # MC sim gauge.
        self.mc_gauge_rx = self.add_gauge(self.panel_rx, panel_sizer, "Monte Carlo simulations:")


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close the window.
        self.Hide()


    def handler_timer(self, event):
        """Event handler for the timer.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Pulse.
        self.main_gauge.Pulse()

        # Stop the timer and update the gauge.
        if not status.exec_lock.locked() and self.timer.IsRunning():
            self.timer.Stop()
            self.update_gauge()


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

        # Set the current data pipe info.
        pipe = cdp_name()
        if pipe == None:
            pipe = ''
        wx.CallAfter(self.cdp.SetValue, str_to_gui(pipe))

        # Set the current GUI analysis info.
        name = self.gui.analysis.current_analysis_name()
        if name == None:
            name = ''
        wx.CallAfter(self.name.SetValue, str_to_gui(name))

        # The analysis type.
        type = self.gui.analysis.current_analysis_type()

        # Rx fitting auto-analysis.
        if type in ['R1', 'R2']:
            wx.CallAfter(self.panel_rx.Show)
            wx.CallAfter(self.update_rx)
        else:
            wx.CallAfter(self.panel_rx.Hide)

        # Model-free auto-analysis.
        if type == 'model-free':
            wx.CallAfter(self.panel_mf.Show)
            wx.CallAfter(self.update_mf)
        else:
            wx.CallAfter(self.panel_mf.Hide)

        # Update the main gauge.
        wx.CallAfter(self.update_gauge)


    def update_gauge(self):
        """Update the main execution gauge."""

        # Pulse during execution.
        if status.exec_lock.locked():
            # Start the timer.
            if not self.timer.IsRunning():
                self.timer.Start(100)

            # Finish.
            return

        # Finished.
        key = self.analysis_key()
        if key and status.auto_analysis.has_key(key) and status.auto_analysis[key].fin:
            # Stop the timer.
            if self.timer.IsRunning():
                self.timer.Stop()

            # Fill the gauge.
            wx.CallAfter(self.main_gauge.SetValue, 100)

        # Gauge is in the initial state, so no need to reset.
        if not self.main_gauge.GetValue():
            return

        # No key, so reset.
        if not key or not status.auto_analysis.has_key(key):
            wx.CallAfter(self.main_gauge.SetValue, 0)

        # Key present, but analysis not started.
        if key and status.auto_analysis.has_key(key) and not status.auto_analysis[key].fin:
            wx.CallAfter(self.main_gauge.SetValue, 0)


    def update_mf(self):
        """Update the model-free specific elements."""

        # The analysis key.
        key = self.analysis_key()
        if not key or not status.auto_analysis.has_key(key):
            return

        # Set the diffusion model.
        wx.CallAfter(self.global_model_mf.SetValue, status.auto_analysis[key].diff_model)

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
                wx.CallAfter(self.progress_gauge_mf.SetValue, percent)

        # Sphere to Ellipsoid Models.
        elif status.auto_analysis[key].diff_model in ['sphere', 'prolate', 'oblate', 'ellipsoid']:
            # The round as a percentage.
            percent = int(100 * (status.auto_analysis[key].round - 1) / status.auto_analysis[key].max_iter)
            if percent > 100:
                percent = 100

            # Update the progress bar.
            wx.CallAfter(self.progress_gauge_mf.SetValue, percent)

        # Monte Carlo simulations.
        if status.auto_analysis[key].mc_number:
            # The simulation number as a percentage.
            percent = int(100 * (status.auto_analysis[key].mc_number + 2) / cdp.sim_number)
            if percent > 100:
                percent = 100

            # Update the progress bar.
            wx.CallAfter(self.mc_gauge_mf.SetValue, percent)


    def update_rx(self):
        """Update the model-free specific elements."""

        # The analysis key.
        key = self.analysis_key()
        if not key or not status.auto_analysis.has_key(key):
            return

        # Monte Carlo simulations.
        if status.auto_analysis[key].mc_number:
            # The simulation number as a percentage.
            percent = int(100 * (status.auto_analysis[key].mc_number + 2) / cdp.sim_number)
            if percent > 100:
                percent = 100

            # Update the progress bar.
            wx.CallAfter(self.mc_gauge_rx.SetValue, percent)



class LogCtrl(wx.stc.StyledTextCtrl):
    """A special control designed to display relax output messages."""

    def __init__(self, parent, log_queue=None, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.BORDER_SUNKEN, name=wx.stc.STCNameStr):
        """Set up the log control.

        @param parent:          The parent wx window object.
        @type parent:           Window
        @keyword log_queue:     The queue of log messages.
        @type log_queue:        Queue.Queue instance
        @keyword id:            The wx ID.
        @type id:               int
        @keyword pos:           The window position.
        @type pos:              Point
        @keyword size:          The window size.
        @type size:             Size
        @keyword style:         The StyledTextCtrl to apply.
        @type style:            long
        @keyword name:          The window name.
        @type name:             str
        """

        # Store the args.
        self.log_queue = log_queue

        # Initialise the base class.
        super(LogCtrl, self).__init__(parent, id=id, pos=pos, size=size, style=style, name=name)

        # Set the font info.
        self.SetFont(font.modern_8)

        # Create the STDERR style (with assignment 1).
        self.StyleSetForeground(1, wx.NamedColour('red'))

        # Create the relax prompt style (assignment 2).
        self.StyleSetForeground(2, wx.NamedColour('blue'))

        # Create the relax warning style (assignment 3).
        self.StyleSetForeground(3, wx.NamedColour('orange red'))

        # Bind events.
        self.Bind(wx.EVT_KEY_DOWN, self.capture_keys)


    def capture_keys(self, event):
        """Control which key events are active, preventing text insertion and deletion.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Allow Ctrl+C events.
        if event.ControlDown() and event.GetKeyCode() == 67:
            event.Skip()


    def get_text(self):
        """Concatenate all of the text from the log queue and return it as a string.

        @return:    A list of the text from the log queue and a list of the streams these correspond to.
        @rtype:     list of str, list of int
        """

        # Initialise.
        string_list = ['']
        stream_list = [0]

        # Loop until the queue is empty.
        while 1:
            # End condition.
            if self.log_queue.empty():
                break

            # Get the data.
            msg, stream = self.log_queue.get()

            # The relax prompt.
            if msg[1:7] == 'relax>':
                # Add a new line to the last block.
                string_list[-1] += '\n'

                # Add the prompt part.
                string_list.append('relax>')
                stream_list.append(2)

                # Shorten the message.
                msg = msg[7:]

                # Start a new section.
                string_list.append('')
                stream_list.append(stream)

            # The relax warnings on STDERR.
            if msg[0:13] == 'RelaxWarning:':
                # Add the warning.
                string_list.append(msg)
                stream_list.append(3)
                continue

            # A different stream.
            if stream_list[-1] != stream:
                string_list.append('')
                stream_list.append(stream)

            # Add the text.
            string_list[-1] = string_list[-1] + msg

        # Return the concatenated text.
        return string_list, stream_list


    def limit_scrollback(self, prune=20):
        """Limit scroll back to the maximum number of lines.

        Lines are deleted in blocks of 'prune' number of lines for faster operation.
        """

        # Maximum not reached, so do nothing.
        if self.GetLineCount() < status.controller_max_entries:
            return

        # Get the current selection, scroll position and caret position.
        pos_start, pos_end = self.GetSelection()
        curr_pos = self.GetCurrentPos()

        # Prune the first x lines.
        del_start = 0
        del_end = self.GetLineEndPosition(prune) + 1
        del_extent = del_end - del_start
        self.SetSelection(del_start, del_end)
        self.DeleteBack()

        # Determine the new settings.
        new_curr_pos = curr_pos - del_extent
        new_pos_start = pos_start - del_extent
        new_pos_end = pos_end - del_extent

        # Return to the original position and state.
        self.SetCurrentPos(new_curr_pos)
        self.SetSelection(new_pos_start, new_pos_end)
        self.LineScroll(0, prune)


    def write(self):
        """Write the text in the log queue to the log control."""

        # Get the text.
        string_list, stream_list = self.get_text()

        # Nothing to do.
        if len(string_list) == 1 and string_list[0] == '':
            return

        # At the end?
        at_end = False
        if self.GetScrollPos(wx.VERTICAL) == self.GetScrollRange(wx.VERTICAL) - self.LinesOnScreen():
            at_end = True

        # Add the text.
        for i in range(len(string_list)):
            # Add the text.
            self.AppendText(string_list[i])

            # The different styles.
            if stream_list[i] != 0:
                # Get the text extents.
                len_string = len(string_list[i].encode('utf8'))
                end = self.GetLength()

                # Change the style.
                self.StartStyling(end - len_string, 31)
                self.SetStyling(len_string, stream_list[i])

        # Limit the scroll back.
        self.limit_scrollback()

        # Stay at the end.
        if at_end:
            self.ScrollToLine(self.GetLineCount())



class Redirect_text(object):
    """The IO redirection to text control object."""

    def __init__(self, control, log_queue, stream=0):
        """Set up the text redirection object.

        @param control:         The text control object to redirect IO to.
        @type control:          wx.TextCtrl instance
        @param log_queue:       The queue of log messages.
        @type log_queue:        Queue.Queue instance
        @keyword stream:        The type of steam (0 for STDOUT and 1 for STDERR).
        @type stream:           int
        """

        # Store the args.
        self.control = control
        self.log_queue = log_queue
        self.stream = stream


    def write(self, string):
        """Simulate the file object write method.

        @param string:  The text to write.
        @type string:   str
        """

        # Debugging print out to the terminal.
        if status.debug:
            if self.stream == 0:
                sys.__stdout__.write(string)
            else:
                sys.__stderr__.write(string)

        # Add the text to the queue.
        self.log_queue.put([string, self.stream])

        # Call the log control write method one the GUI is responsive.
        wx.CallAfter(self.control.write)
