###############################################################################
#                                                                             #
# Copyright (C) 2010-2014 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Base class module for the wizard GUI elements."""

# Python module imports.
import wx
from wx.lib import buttons, scrolledpanel

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from graphics import IMAGE_PATH, fetch_icon
from gui.fonts import font
from gui.icons import relax_icons
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.misc import add_border, bitmap_setup
from gui.string_conv import float_to_gui, str_to_gui
from lib.check_types import is_float
from lib.errors import RelaxImplementError
from status import Status; status = Status()


class Wiz_page(wx.Panel):
    """The wizard pages to be placed inside the wizard.

    To inherit from this class, you must minimally supply the add_contents() method.  This method should build the specific GUI elements.  The following methods are also designed to be overwritten:

        - add_artwork(), this builds the left hand artwork section of the page.
        - add_contents(), this builds the right hand section of the page.
        - on_display(), this is executed when the page is displayed.
        - on_display_post(), this is executed when the page is displayed, directly after the on_display method.
        - on_execute(), this is executed when the wizard is terminated or the apply button is hit.
        - on_next(), this is executed when moving to the next wizard page.

    The following methods can be used by add_contents() to create standard GUI elements:

        - chooser()
        - combo_box()
        - file_selection()
        - input_field()
        - text()

    These are described in full detail in their docstrings.
    """

    # Some class variables.
    art_spacing = 20
    divider = None
    height_element = 27
    image_path = IMAGE_PATH + "relax.gif"
    main_text = ''
    setup_fail = False
    size_button = (100, 33)
    size_square_button = (33, 33)
    title = ''

    def __init__(self, parent, height_desc=220):
        """Set up the window.

        @param parent:          The parent GUI element.
        @type parent:           wx.object instance
        @keyword height_desc:   The height in pixels of the description part of the wizard.
        @type height_desc:      int or None
        """

        # Store the args.
        self.parent = parent
        self.height_desc = height_desc

        # Execute the base class method.
        wx.Panel.__init__(self, parent, id=-1)

        # Initilise some variables.
        self.exec_status = False

        # The wizard GUI element storage.
        self._elements = {}

        # Pack a sizer into the panel.
        box_main = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(box_main)

        # Add the artwork.
        self.add_artwork(box_main)

        # The size of the image.
        image_x, image_y = self.image.GetSize()

        # Calculate the size of the main section, and the subdivisions.
        self._main_size = parent._size_x - image_x - self.art_spacing - 2*parent._border
        if self.divider:
            self._div_left = self.divider
            self._div_right = self._main_size - self.divider
        else:
            self._div_left = self._div_right = self._main_size / 2

        # Add the main sizer.
        main_sizer = self._build_main_section(box_main)

        # Add the title.
        self._add_title(main_sizer)

        # Add the description.
        self.add_desc(main_sizer, max_y=self.height_desc)

        # Add the specific GUI elements (bounded by spacers).
        main_sizer.AddStretchSpacer()
        self.add_contents(main_sizer)


    def _add_title(self, sizer):
        """Add the title to the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Spacing.
        sizer.AddSpacer(10)

        # The text.
        title = wx.StaticText(self, -1, self.title)

        # Font.
        title.SetFont(font.title)

        # Add the title.
        sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 0)

        # Spacing.
        sizer.AddSpacer(10)


    def _apply(self, event=None):
        """Apply the operation.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # A bit of user feedback.
        wx.BeginBusyCursor()

        # Execute.
        self.exec_status = self.on_execute()

        # Execution failure.
        if not self.exec_status:
            if wx.IsBusy():
                wx.EndBusyCursor()
            return

        # Finished.
        self.on_completion()

        # Execute the on_apply() method.
        self.on_apply()

        # Turn off the busy cursor if needed.
        if wx.IsBusy():
            wx.EndBusyCursor()


    def _build_main_section(self, sizer):
        """Add the main part of the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        @return:        The sizer object for the main part of the dialog.
        @rtype:         wx.Sizer instance
        """

        # Use a grid sizer for packing the elements.
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Pack the sizer.
        sizer.Add(main_sizer, 1, wx.EXPAND|wx.ALL, 0)

        # Return the sizer.
        return main_sizer


    def add_artwork(self, sizer):
        """Add the artwork to the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add the graphics.
        if self.image_path:
            self.image = wx.StaticBitmap(self, -1, bitmap_setup(self.image_path))
            sizer.Add(self.image, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 0)

        # A spacer.
        sizer.AddSpacer(self.art_spacing)


    def add_contents(self, sizer):
        """Add the specific GUI elements (dummy method).

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # This must be supplied.
        raise RelaxImplementError


    def add_desc(self, sizer, max_y=220):
        """Add the description to the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        @keyword max_y: The maximum height, in number of pixels, for the description.
        @type max_y:    int
        """

        # A line with spacing.
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 0)
        sizer.AddSpacer(5)

        # Create a scrolled panel.
        panel = scrolledpanel.ScrolledPanel(self, -1, name="desc")

        # A sizer for the panel.
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # The text.
        text = wx.StaticText(panel, -1, self.main_text, style=wx.TE_MULTILINE)
        text.SetFont(font.normal)

        # Wrap the text.
        text.Wrap(self._main_size - 20)

        # The text size.
        x, y = text.GetSizeTuple()

        # Scrolling needed.
        if y > max_y-10:
            # Set the panel size.
            panel.SetInitialSize((self._main_size, max_y))

        # No scrolling.
        else:
            # Rewrap the text.
            text.Wrap(self._main_size)

            # Set the panel size.
            panel.SetInitialSize(text.GetSize())

        # Add the text.
        panel_sizer.Add(text, 0, wx.ALIGN_LEFT, 0)

        # Set up and add the panel to the sizer.
        panel.SetSizer(panel_sizer)
        panel.SetAutoLayout(1)
        panel.SetupScrolling(scroll_x=False, scroll_y=True)
        sizer.Add(panel, 0, wx.ALL|wx.EXPAND)

        # A line with spacing.
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 0)
        sizer.AddSpacer(5)


    def on_apply(self):
        """To be over-ridden if an action is to be performed on hitting the apply button.

        This method will be called when clicking on the apply button.
        """


    def on_back(self):
        """To be over-ridden if an action is to be performed just before moving back to the previous page.

        This method is called when moving back to the previous page of the wizard.
        """


    def on_completion(self):
        """To be over-ridden if an action is to be performed just after executing self.on_execute().

        This method is called just after self.on_execute() has been called
        """


    def on_display(self):
        """To be over-ridden if an action is to be performed prior to displaying the page.

        This method will be called by the wizard class method _display_page() just after hiding all other pages but prior to displaying this page.
        """


    def on_display_post(self):
        """To be over-ridden if an action is to be performed after the execution of the on_display() method.

        This method will be called by the wizard class method _display_page() just after hiding all other pages but prior to displaying this page.
        """


    def on_execute(self):
        """To be over-ridden if an action is to be performed just before exiting the page.

        This method is called when terminating the wizard or hitting the apply button.
        """

        return True


    def on_init(self):
        """To be over-ridden if an action is to be performed when a page is newly displayed.

        This method will be called by the wizard class method _display_page() at the very end.
        """


    def on_next(self):
        """To be over-ridden if an action is to be performed just before moving to the next page.

        This method is called when moving to the next page of the wizard.
        """



class Wiz_window(wx.Dialog):
    """The wizard."""

    # Some class variables.
    _size_button = (100, 33)
    ICON_APPLY = fetch_icon('oxygen.actions.dialog-ok-apply', "22x22")
    ICON_BACK = fetch_icon('oxygen.actions.go-previous-view', "22x22")
    ICON_CANCEL = fetch_icon('oxygen.actions.dialog-cancel', "22x22")
    ICON_FINISH = fetch_icon('oxygen.actions.dialog-ok', "22x22")
    ICON_NEXT = fetch_icon('oxygen.actions.go-next-view', "22x22")
    ICON_OK = fetch_icon('oxygen.actions.dialog-ok', "22x22")
    ICON_SKIP = fetch_icon('oxygen.actions.arrow-right-double-relax-blue', "22x22")
    TEXT_APPLY = " Apply"
    TEXT_BACK = " Back"
    TEXT_CANCEL = " Cancel"
    TEXT_FINISH = " Finish"
    TEXT_NEXT = " Next"
    TEXT_OK = " OK"
    TEXT_SKIP = " Skip"


    def __init__(self, parent=None, size_x=400, size_y=400, title='', border=10, style=wx.DEFAULT_DIALOG_STYLE):
        """Set up the window.

        @keyword parent:    The parent window.
        @type parent:       wx.Window instance
        @keyword size_x:    The width of the wizard.
        @type size_x:       int
        @keyword size_y:    The height of the wizard.
        @type size_y:       int
        @keyword title:     The title of the wizard dialog.
        @type title:        str
        @keyword border:    The size of the border inside the wizard.
        @type border:       int
        @keyword style:     The dialog style.
        @type style:        wx style
        """

        # Store the args.
        self._size_x = size_x
        self._size_y = size_y
        self._border = border

        # Execute the base class method.
        wx.Dialog.__init__(self, parent, id=-1, title=title, style=style)

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # The sizer for the dialog.
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Build the central sizer, with borders.
        self._main_sizer = add_border(sizer, border=border, packing=wx.VERTICAL)

        # Set the default size of the dialog.
        self.SetSize((size_x, size_y))

        # Centre the dialog.
        self.Centre()

        # Initialise the page storage.
        self._current_page = 0
        self._num_pages = 0
        self._pages = []
        self._page_sizers = []
        self._button_sizers = []
        self._button_apply_flag = []
        self._button_skip_flag = []
        self._buttons = []
        self._button_ids = []
        self._exec_on_next = []
        self._exec_count = []
        self._proceed_on_error = []
        self._uf_flush = []
        self._seq_fn_list = []
        self._seq_next = []
        self._seq_prev = []
        self._skip_flag = []

        # A max of 15 pages should be enough.
        for i in range(15):
            # Append some Nones.
            self._pages.append(None)

            # Initialise all box sizers for the wizard pages.
            self._page_sizers.append(wx.BoxSizer(wx.VERTICAL))

            # Initialise all box sizers for the buttons.
            self._button_sizers.append(wx.BoxSizer(wx.HORIZONTAL))

            # Set all button flags.
            self._button_apply_flag.append(True)
            self._button_skip_flag.append(False)

            # Initialise the button storage.
            self._buttons.append({'back': None,
                                  'apply': None,
                                  'next': None,
                                  'ok': None,
                                  'finish': None,
                                  'cancel': None})

            # Initialise a set of unique button IDs.
            self._button_ids.append({'back': wx.NewId(),
                                     'apply': wx.NewId(),
                                     'next': wx.NewId(),
                                     'ok': wx.NewId(),
                                     'finish': wx.NewId(),
                                     'cancel': wx.NewId()})

            # Execute on next by default.
            self._exec_on_next.append(True)

            # Execution count.
            self._exec_count.append(0)

            # Proceed to next page on errors by default.
            self._proceed_on_error.append(True)

            # No user function flushing of the GUI interpreter thread prior to proceeding.
            self._uf_flush.append(False)

            # Page sequence initialisation.
            self._seq_fn_list.append(self._next_fn)
            self._seq_next.append(None)
            self._seq_prev.append(None)

            # Page skipping.
            self._skip_flag.append(False)

        # Flag to suppress later button addition.
        self._buttons_built = False

        # Bind some events.
        self.Bind(wx.EVT_CLOSE, self._handler_close)

        # ESC to exit, via an accelerator table which creates menu events.
        id = wx.NewId()
        self.acc_list = [(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, id)]
        self.acc_table = wx.AcceleratorTable(self.acc_list)
        self.SetAcceleratorTable(self.acc_table)
        self.Bind(wx.EVT_MENU, self._handler_escape, id=self.acc_list[0][2])


    def _apply(self, event=None):
        """Execute the current page's 'Apply' method.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Execute the current page's apply() method.
        self._pages[self._current_page]._apply()


    def _build_buttons(self):
        """Construct the buttons for all pages of the wizard."""

        # Loop over each page.
        for i in range(self._num_pages):
            # The back button (only for multi-pages, after the first).
            if self._num_pages > 1 and i > 0:
                # Create the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_BACK)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_BACK, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Return to the previous page")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._go_back, button)
                self._buttons[i]['back'] = button

                # Spacer.
                self._button_sizers[i].AddSpacer(5)

            # The apply button.
            if self._button_apply_flag[i]:
                # Create the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_APPLY)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_APPLY, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Apply the operation")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._pages[i]._apply, button)
                self._buttons[i]['apply'] = button

                # Spacer.
                self._button_sizers[i].AddSpacer(5)

            # The skip button.
            if self._button_skip_flag[i]:
                # Create the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_SKIP)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_SKIP, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Skip the operation")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._skip, button)
                self._buttons[i]['skip'] = button

                # Spacer.
                self._button_sizers[i].AddSpacer(5)

            # The next button (only for multi-pages, excluding the last).
            if self._num_pages > 1 and i < self._num_pages - 1:
                # Create the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_NEXT)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_NEXT, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Move to the next page")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._go_next, button)
                self._buttons[i]['next'] = button

            # The OK button (only for single pages).
            if self._num_pages == 1:
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_OK)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_OK, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Accept the operation")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._ok, button)
                self._buttons[i]['ok'] = button

            # The finish button (only for the last page with multi-pages).
            if self._num_pages > 1 and i == self._num_pages - 1:
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_FINISH)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_FINISH, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Accept the operation")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._ok, button)
                self._buttons[i]['finish'] = button

            # Spacer.
            self._button_sizers[i].AddSpacer(15)

            # The cancel button.
            button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_CANCEL)
            button.SetBitmapLabel(wx.Bitmap(self.ICON_CANCEL, wx.BITMAP_TYPE_ANY))
            button.SetFont(font.normal)
            button.SetToolTipString("Abort the operation")
            button.SetMinSize(self._size_button)
            self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
            self.Bind(wx.EVT_BUTTON, self._cancel, button)
            self._buttons[i]['cancel'] = button

        # Flag to suppress later button addition.
        self._buttons_built = True


    def _cancel(self, event=None):
        """Cancel the operation.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Execute the page's on_next() method to allow the page to clean itself up.
        self._pages[self._current_page].on_next()

        # Close the window.
        self.Close()


    def _display_page(self, i):
        """Display the given page.

        @param i:   The index of the page to display.
        @type i:    int
        """

        # Hide all of the original contents.
        for j in range(self._num_pages):
            if self._main_sizer.IsShown(self._page_sizers[j]):
                self._main_sizer.Hide(self._page_sizers[j])

        # Show the desired page.
        if status.show_gui:
            self._main_sizer.Show(self._page_sizers[i])

        # Execute the page's on_display() method.
        self._pages[i].on_display()
        self._pages[i].on_display_post()

        # Re-perform the window layout.
        self.Layout()
        self.Refresh()

        # Execute the page's on_init() method.
        self._pages[i].on_init()

        # Set the focus to this page to allow the keyboard to be functional without a mouse click.
        self._pages[i].SetFocus()


    def _go_back(self, event=None):
        """Return to the previous page.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Execute the page's on_next() method.
        self._pages[self._current_page].on_back()

        # Work back in the sequence.
        self._current_page = self._seq_prev[self._current_page]

        # Display the previous page.
        self._display_page(self._current_page)


    def _go_next(self, event=None):
        """Move to the next page.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Execute the page's on_next() method.
        self._pages[self._current_page].on_next()

        # Operations for non-skipped pages.
        if not self._skip_flag[self._current_page]:
            # Execute the page's on_execute() method (via the _apply() method).
            if self._exec_on_next[self._current_page]:
                self._pages[self._current_page]._apply(event)

                # UF flush.
                if self._uf_flush[self._current_page]:
                    interpreter.flush()

                # Check for execution errors.
                if not self._pages[self._current_page].exec_status:
                    # Do not proceed.
                    if not self._proceed_on_error[self._current_page]:
                        return

                # Increment the execution counter.
                self._exec_count[self._current_page] += 1

        # Determine the next page.
        next_page = self._seq_fn_list[self._current_page]()

        # No next page, so terminate.
        if self._pages[next_page] == None:
            self._ok(None)
            return

        # Update the sequence lists.
        self._seq_next[self._current_page] = next_page
        self._seq_prev[next_page] = self._current_page

        # Change the current page.
        self._current_page = next_page

        # Display the next page.
        self._display_page(self._current_page)


    def _handler_close(self, event=None):
        """Event handler for the close window action.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Execute the page's on_next() method to allow the page to clean itself up.
        self._pages[self._current_page].on_next()

        # Continue with the window closing.
        event.Skip()


    def _handler_escape(self, event=None):
        """Event handler for key strokes.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Close the window.
        self.Close()


    def _next_fn(self):
        """Standard function for setting the next page to the one directly next in the sequence.

        @return:    The index of the next page, which is the current page index plus one.
        @rtype:     int
        """

        # Return the next page.
        return self._current_page + 1


    def _ok(self, event=None):
        """Accept the operation.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Loop over the pages in the sequence and execute their _apply() methods, if not already done and not skipped.
        for i in self._seq_loop():
            if not self._exec_count[i] and not self._skip_flag[i]:
                # Execute the _apply method.
                self._pages[i]._apply(event)

                # UF flush.
                if self._uf_flush[i]:
                    interpreter.flush()

                # Check for execution errors.
                if not self._pages[self._current_page].exec_status:
                    # Do not proceed.
                    if not self._proceed_on_error[self._current_page]:
                        return

                # Increment the execution counter.
                self._exec_count[i] += 1

        # Execute the current page's on_next() method to allow the page to clean itself up.
        self._pages[self._current_page].on_next()

        # Then close the dialog.
        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.Close()


    def _seq_loop(self):
        """Loop over the sequence in the forwards direction."""

        # Initialise.
        current = 0

        # First yield the initial element (always zero!).
        yield current

        # Loop over the sequence.
        while True:
            # Update.
            next = self._seq_next[current]
            current = next

            # End of the sequence.
            if next == None:
                break

            # Yield the next index.
            yield next


    def _skip(self, event=None):
        """Skip the page.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Set the skip flag.
        self._skip_flag[self._current_page] = True

        # Go to the next page.
        self._go_next(None)


    def add_page(self, panel, apply_button=True, skip_button=False, exec_on_next=True, proceed_on_error=True, uf_flush=False):
        """Add a new page to the wizard.

        @param panel:               The page to add to the wizard.
        @type panel:                wx.Panel instance
        @keyword apply_button:      A flag which if true will show the apply button for that page.
        @type apply_button:         bool
        @keyword skip_button:       A flag which if true will show the skip button for that page.
        @type skip_button:          bool
        @keyword exec_on_next:      A flag which if true will run the on_execute() method when clicking on the next button.
        @type exec_on_next:         bool
        @keyword proceed_on_error:  A flag which if True will proceed to the next page (or quit if there are no more pages) despite the occurrence of an error in execution.  If False, the page will remain open (the GUI interpreter thread will be flushed first to synchronise).
        @type proceed_on_error:     bool
        @keyword uf_flush:          A flag which if True will cause the GUI interpreter thread to be flushed to clear out all user function call prior to proceeding.
        @type uf_flush:             bool
        @return:                    The index of the page in the wizard.
        @rtype:                     int
        """

        # Store the page.
        index = self._num_pages
        self._num_pages += 1
        self._pages[index] = panel

        # Store a new sizer for the page and its buttons.
        self._main_sizer.Add(self._page_sizers[index], 1, wx.ALL|wx.EXPAND, 0)

        # Add the sizer for the top half.
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        self._page_sizers[index].Add(top_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Add the page to the top sizer.
        top_sizer.Add(panel, 1, wx.ALL|wx.EXPAND, 0)

        # Add the sizer for the wizard buttons.
        self._page_sizers[index].Add(self._button_sizers[index], 0, wx.ALIGN_RIGHT|wx.ALL, 0)

        # Store the flags.
        self._button_apply_flag[index] = apply_button
        self._button_skip_flag[index] = skip_button
        self._exec_on_next[index] = exec_on_next
        self._proceed_on_error[index] = proceed_on_error
        if not proceed_on_error or uf_flush:
            self._uf_flush[index] = True

        # Store the index of the page.
        panel.page_index = self._num_pages - 1

        # Return the index of the page.
        return panel.page_index


    def block_next(self, block=True):
        """Prevent moving forwards (or unblock).

        @keyword block: A flag which if True will block forwards movement and if False will unblock.
        @type block:    bool
        """

        # The buttons to disable.
        buttons = ['next', 'ok', 'finish']

        # Disable or enable the buttons.
        for i in range(len(buttons)):
            # The button.
            button = self._buttons[self._current_page][buttons[i]]
            if button == None:
                continue

            # Block.
            if block:
                button.Disable()

            # Unblock.
            else:
                button.Enable()


    def get_page(self, index):
        """Get a page from the wizard.

        @param index:   The index of the page.
        @type index:    int
        @return:        The page object.
        @rtype:         Wiz_page instance.
        """

        # Return the page.
        return self._pages[index]


    def reset(self):
        """Reset the wizard."""

        # Clear the execution counts.
        for i in range(len(self._exec_count)):
            self._exec_count[i] = 0


    def run(self, modal=False):
        """Execute the wizard.

        @keyword modal: A flag which if True will cause the wizard to be run as a modal dialog.
        @type modal:    bool
        @return:        The status from the modal operation, i.e. True if the wizard is run, False if cancelled or other error occur.  For modeless operation, this returns nothing.
        @rtype:         bool or None
        """

        # Check that all pages have been set up correctly, returning without doing anything if not.
        for i in range(self._num_pages):
            if self._pages[i].setup_fail:
                return

        # Build the buttons for the entire wizard.
        if not self._buttons_built:
            self._build_buttons()

        # Display the first page.
        self._display_page(0)

        # Display failure.
        if self._pages[0].setup_fail:
            return

        # No GUI.
        if not status.show_gui:
            return

        # Modal operation.
        if modal:
            # Show the wizard (it should be closed by the _cancel() or _ok() methods).
            wiz_status = self.ShowModal()

            # Return the status.
            return wiz_status

        # Modeless operation.
        else:
            # Show the wizard.
            self.Show()


    def set_seq_next_fn(self, index, fn):
        """A user specified function for non-linear page changing.

        @param index:   The index of the page the function should be associated with.
        @type index:    int
        @param fn:      The function for determining the page after the current.  This function should return the index of the next page.
        @type fn:       func or method.
        """

        # Store the function.
        self._seq_fn_list[index] = fn


    def setup_page(self, page=None, **kargs):
        """Allow a specified user function page to be remotely set up.

        @keyword page:  The page to setup.  This is the page index key.
        @type page:     str
        """

        # Get the page.
        page = self.get_page(self.page_indices[page])

        # Loop over the keyword arguments and set them.
        for arg in kargs:
            # The value.
            value = kargs[arg]
            if isinstance(value, str):
                value = str_to_gui(value)
            elif is_float(value):
                value = float_to_gui(value)

            # Set the argument.
            page.SetValue(arg, value)
