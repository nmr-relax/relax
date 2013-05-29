###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
# Copyright (C) 2010-2013 Edward d'Auvergne                                   #
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
"""Module containing the base class for the automatic R1 and R2 analysis frames."""

# Python module imports.
from os import sep
import wx
from wx.lib import scrolledpanel

# relax module imports.
from pipe_control.mol_res_spin import are_spins_named
from status import Status; status = Status()

# relax GUI module imports.
from gui.fonts import font
from gui.message import Question
from gui.misc import format_table
from gui import paths
from gui.string_conv import gui_to_str
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from gui.wizards.wiz_objects import Wiz_page, Wiz_window
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.data import Uf_tables; uf_tables = Uf_tables()


class Peak_intensity_wizard(Wiz_window):
    """The wizard for loading peak intensity data."""

    def __init__(self, parent=None, size_x=1000, size_y=750, title="Peak intensity loading wizard", noe=False, relax_fit=False, relax_disp=False, relax_disp_cpmg=False, relax_disp_times=False):
        """Set up the peak intensity loading wizard.

        @keyword parent:            The parent window.
        @type parent:               wx.Window instance
        @keyword size_x:            The width of the wizard.
        @type size_x:               int
        @keyword size_y:            The height of the wizard.
        @type size_y:               int
        @keyword title:             The title of the wizard dialog.
        @type title:                str
        @keyword noe:               A flag which when True will enable the steady-state NOE portions of the wizard.
        @type noe:                  bool
        @keyword relax_fit:         A flag which when True will enable the relaxation curve-fitting portions of the wizard.
        @type relax_fit:            bool
        @keyword relax_disp:        A flag which when True will enable the relaxation dispersion portions of the wizard.
        @type relax_disp:           bool
        @keyword relax_disp_cpmg:   A flag which if True enables the relax_disp.cpmg_frq user function and if False enables the relax_disp.spin_lock_field user function.
        @type relax_disp_cpmg:      bool
        @keyword relax_disp_times:  A flag which if True will enable the relax_disp.relax_time page.
        @type relax_disp_times:     bool
        """

        # Store the args.
        self.noe_flag = noe
        self.relax_fit_flag = relax_fit
        self.relax_disp_flag = relax_disp
        self.relax_disp_cpmg = relax_disp_cpmg
        self.relax_disp_times = relax_disp_times

        # Get the app and store the GUI instance.
        app = wx.GetApp()
        self.gui = app.gui

        # Execute the base class method.
        Wiz_window.__init__(self, parent=self.gui, size_x=size_x, size_y=size_y, title=title, style=wx.DEFAULT_DIALOG_STYLE)

        # Change the cursor to busy.
        wx.BeginBusyCursor()

        # Initialise the page_indices structure.
        self.page_indices = {}

        # First check that at least a single spin is named!
        if not are_spins_named():
            # The message.
            msg = "No spins have been named.  Please use the spin.name user function first, otherwise it is unlikely that any data will be loaded from the peak intensity file.\n\nThis message can be ignored if the generic file format is used and spin names have not been specified.  Would you like to name the spins already loaded into the relax data store?"

            # Ask about naming spins, and add the spin.name user function page.
            if (status.show_gui and Question(msg, title="Incomplete setup", size=(450, 250), default=True).ShowModal() == wx.ID_YES) or not status.show_gui:
                page = uf_store['spin.name'].create_page(self, sync=True)
                self.page_indices['name'] = self.add_page(page, proceed_on_error=False)

        # The spectrum.read_intensities page.
        self.page_intensity = uf_store['spectrum.read_intensities'].create_page(self, sync=True)
        self.page_indices['read'] = self.add_page(self.page_intensity, skip_button=True, proceed_on_error=False)

        # Error type selection page.
        self.page_error_type = Spectral_error_type_page(parent=self, height_desc=520)
        self.page_indices['err_type'] = self.add_page(self.page_error_type, apply_button=False)
        self.set_seq_next_fn(self.page_indices['err_type'], self.wizard_page_after_error_type)

        # The spectrum.replicated page.
        page = uf_store['spectrum.replicated'].create_page(self, sync=True)
        self.page_indices['repl'] = self.add_page(page, skip_button=True, proceed_on_error=False)
        self.set_seq_next_fn(self.page_indices['repl'], self.wizard_page_after_repl)
        page.on_init = self.wizard_update_repl

        # The spectrum.baseplane_rmsd page.
        page = uf_store['spectrum.baseplane_rmsd'].create_page(self, sync=True)
        self.page_indices['rmsd'] = self.add_page(page, skip_button=True, proceed_on_error=False)
        self.set_seq_next_fn(self.page_indices['rmsd'], self.wizard_page_after_rmsd)
        page.on_init = self.wizard_update_rmsd

        # The spectrum.integration_points page.
        page = uf_store['spectrum.integration_points'].create_page(self, sync=True)
        self.page_indices['pts'] = self.add_page(page, skip_button=True, proceed_on_error=False)
        page.on_init = self.wizard_update_pts

        # NOE pages.
        if self.noe_flag:
            # The noe.spectrum_type page.
            page = uf_store['noe.spectrum_type'].create_page(self, sync=True)
            self.page_indices['spectrum_type'] = self.add_page(page, skip_button=False, proceed_on_error=False)
            page.on_display_post = self.wizard_update_noe_spectrum_type

        # Relaxation curve-fitting pages.
        if self.relax_fit_flag:
            # The relax_fit.relax_time page.
            page = uf_store['relax_fit.relax_time'].create_page(self, sync=True)
            self.page_indices['relax_time'] = self.add_page(page, skip_button=False, proceed_on_error=False)
            page.on_init = self.wizard_update_relax_fit_relax_time

        # Relaxation dispersion pages.
        if self.relax_disp_flag:
            # The spectrometer.frequency page.
            page = uf_store['spectrometer.frequency'].create_page(self, sync=True)
            self.page_indices['spectrometer_frequency'] = self.add_page(page, skip_button=True, proceed_on_error=False)
            page.on_init = self.wizard_update_spectrometer_frequency

            # The relax_disp.relax_time page.
            if self.relax_disp_times:
                page = uf_store['relax_disp.relax_time'].create_page(self, sync=True)
                self.page_indices['relax_time'] = self.add_page(page, skip_button=True, proceed_on_error=False)
                page.on_init = self.wizard_update_relax_disp_relax_time

            # CPMG pages.
            if self.relax_disp_cpmg:
                # The relax_disp.cpmg_frq page.
                page = uf_store['relax_disp.cpmg_frq'].create_page(self, sync=True)
                self.page_indices['cpmg_frq'] = self.add_page(page, skip_button=False, proceed_on_error=False)
                page.on_init = self.wizard_update_relax_disp_cpmg_frq

            # R1rho pages.
            else:
                # The relax_disp.spin_lock_field page.
                page = uf_store['relax_disp.spin_lock_field'].create_page(self, sync=True)
                self.page_indices['spin_lock_field'] = self.add_page(page, skip_button=False, proceed_on_error=False)
                page.on_init = self.wizard_update_relax_disp_spin_lock_field

        # Reset the cursor.
        if wx.IsBusy():
            wx.EndBusyCursor()

        # Run the wizard.
        self.run()


    def wizard_page_after_error_type(self):
        """Set the page after the error type choice.

        @return:    The index of the next page, which is the current page index plus one.
        @rtype:     int
        """

        # Go to the spectrum.baseplane_rmsd page.
        if self.page_error_type.selection == 'rmsd':
            return self.page_indices['rmsd']

        # Go to the spectrum.replicated page.
        elif self.page_error_type.selection == 'repl':
            return self.page_indices['repl']


    def wizard_page_after_repl(self):
        """Set the page that comes after the spectrum.replicated page.

        @return:    The index of the next page.
        @rtype:     int
        """

        # Go to the spectrum.integration_points page.
        int_method = gui_to_str(self.page_intensity.uf_args['int_method'].GetValue())
        if int_method != 'height':
            return self.page_indices['pts']

        # Skip to the noe.spectrum_type page.
        elif self.noe_flag:
            return self.page_indices['spectrum_type']

        # Skip to the relax_fit.relax_time page.
        elif self.relax_fit_flag:
            return self.page_indices['relax_time']

        # Skip to the first dispersion page.
        elif self.relax_disp_flag:
            return self.page_indices['spectrometer_frequency']

        # Nothing left, so run off the end.
        else:
            return self._num_pages + 1


    def wizard_page_after_rmsd(self):
        """Set the page that comes after the spectrum.baseplane_rmsd page.

        @return:    The index of the next page.
        @rtype:     int
        """

        # Go to the spectrum.integration_points page.
        int_method = gui_to_str(self.page_intensity.uf_args['int_method'].GetValue())
        if int_method != 'height':
            return self.page_indices['pts']

        # Skip to the noe.spectrum_type page.
        elif self.noe_flag:
            return self.page_indices['spectrum_type']

        # Skip to the relax_fit.relax_time page.
        elif self.relax_fit_flag:
            return self.page_indices['relax_time']

        # Skip to the first dispersion page.
        elif self.relax_disp_flag:
            return self.page_indices['spectrometer_frequency']

        # Nothing left, so run off the end.
        else:
            return self._num_pages + 1


    def wizard_update_ids(self, page_key=None, arg_key='spectrum_id', index=None):
        """Update the spectrum ID on the page specified by the key based on previous data.

        @keyword page_key:  The key of the page to update.
        @type page_key:     str
        @keyword arg_key:   The key of the page argument to change to the spectrum ID.
        @type arg_key:      str
        @keyword index:     The index for list type structures.
        @type index:        None or int
        """

        # The spectrum.read_intensities page.
        page = self.get_page(self.page_indices['read'])

        # Set the spectrum ID.
        id = page.uf_args['spectrum_id'].GetValue()

        # Set the ID in the page.
        page = self.get_page(self.page_indices[page_key])
        if index == None:
            page.uf_args[arg_key].SetValue(id)
        else:
            page.uf_args[arg_key].SetValue(value=id, index=index)


    def wizard_update_noe_spectrum_type(self):
        """Update the noe.spectrum_type page based on previous data."""

        # Update the spectrum ID.
        self.wizard_update_ids(page_key='spectrum_type')


    def wizard_update_pts(self):
        """Update the spectrum.replicated page based on previous data."""

        # Update the spectrum ID.
        self.wizard_update_ids(page_key='pts')


    def wizard_update_relax_disp_cpmg_frq(self):
        """Update the relax_disp.cpmg_frq page based on previous data."""

        # Update the spectrum ID.
        self.wizard_update_ids(page_key='cpmg_frq')


    def wizard_update_relax_disp_relax_time(self):
        """Update the relax_disp.relax_time page based on previous data."""

        # Update the spectrum ID.
        self.wizard_update_ids(page_key='relax_time')


    def wizard_update_relax_disp_spin_lock_field(self):
        """Update the relax_disp.spin_lock_field page based on previous data."""

        # Update the spectrum ID.
        self.wizard_update_ids(page_key='spin_lock_field')


    def wizard_update_relax_fit_relax_time(self):
        """Update the relax_fit.relax_time page based on previous data."""

        # Update the spectrum ID.
        self.wizard_update_ids(page_key='relax_time')


    def wizard_update_repl(self):
        """Update the spectrum.replicated page based on previous data."""

        # Update the spectrum ID.
        self.wizard_update_ids(page_key='repl', arg_key='spectrum_ids', index=0)


    def wizard_update_rmsd(self):
        """Update the spectrum.baseplane_rmsd page based on previous data."""

        # Update the spectrum ID.
        self.wizard_update_ids(page_key='rmsd')


    def wizard_update_spectrometer_frequency(self):
        """Update the spectrometer.frequency page based on previous data."""

        # Update the spectrum ID.
        self.wizard_update_ids(page_key='spectrometer_frequency', arg_key='id')



class Spectral_error_type_page(Wiz_page):
    """The peak intensity reading wizard page for specifying the type of error to be used."""

    # Class variables.
    image_path = paths.WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'
    title = "Specify the type of error to be used"
    main_text = "Please specify from where the peak intensity errors will be obtained.  The is required for the execution of the spectrum.error_analysis user function which will be postponed until after clicking on the 'Execute relax' button at the end of the automatic analysis page.  To understand how the errors will be propagated and analysed, the main parts of the spectrum.error_analysis user function description are given below."
    uf_path = ['spectrum', 'error_analysis']

    def _on_select(self, event):
        """Handle the radio button switching.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The button.
        button = event.GetEventObject()

        # RMSD.
        if button == self.radio_rmsd:
            self.selection = 'rmsd'
        elif button == self.radio_repl:
            self.selection = 'repl'


    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # A box sizer for placing the box sizer in.
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer2, 1, wx.ALL|wx.EXPAND, 0)

        # Bottom spacing.
        sizer.AddStretchSpacer()

        # A bit of indentation.
        sizer2.AddStretchSpacer()

        # A vertical sizer for the radio buttons.
        sizer_radio = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(sizer_radio, 1, wx.ALL|wx.EXPAND, 0)

        # The RMSD radio button.
        self.radio_rmsd = wx.RadioButton(self, -1, "Baseplane RMSD.", style=wx.RB_GROUP)
        sizer_radio.Add(self.radio_rmsd, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacing.
        sizer_radio.AddSpacer(10)

        # The replicated spectra radio button.
        self.radio_repl = wx.RadioButton(self, -1, "Replicated spectra.")
        sizer_radio.Add(self.radio_repl, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Bind the buttons.
        self.Bind(wx.EVT_RADIOBUTTON, self._on_select, self.radio_rmsd)
        self.Bind(wx.EVT_RADIOBUTTON, self._on_select, self.radio_repl)

        # Right side spacing.
        sizer2.AddStretchSpacer(3)

        # Bottom spacing.
        sizer.AddStretchSpacer()

        # Set the default selection.
        self.selection = 'rmsd'


    def add_desc(self, sizer, max_y=520):
        """Add the description to the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        @keyword max_y: The maximum height, in number of pixels, for the description.
        @type max_y:    int
        """

        # Initialise.
        spacing = 15

        # A line with spacing.
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 0)
        sizer.AddSpacer(5)

        # Create a scrolled panel.
        panel = scrolledpanel.ScrolledPanel(self, -1, name="desc")

        # A sizer for the panel.
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # Initialise the text elements.
        tot_y = 0
        text_elements = []
        text_types = []

        # The wrapped text.
        text = wx.StaticText(panel, -1, self.main_text, style=wx.TE_MULTILINE)
        text.SetFont(font.normal)
        text.Wrap(self._main_size - 20)
        text_elements.append(text)
        text_types.append('title')

        # The text size, then spacing.
        x, y = text.GetSizeTuple()
        tot_y += y
        tot_y += spacing

        # Get the spectrum.error_analysis user function data object.
        uf_data = uf_info.get_uf('spectrum.error_analysis')

        # The description sections.
        if uf_data.desc != None:
            # Loop over the sections.
            for i in range(len(uf_data.desc)):
                # Alias.
                desc = uf_data.desc[i]

                # Skip the prompt examples.
                if desc.get_title() == 'Prompt examples':
                    continue

                # Loop over the text elements.
                for type, element in desc.element_loop(title=True):
                    # The text version of the elements.
                    text = ''
                    if isinstance(element, str):
                        text = element

                    # Format the tables.
                    if type == 'table':
                        text = format_table(uf_tables.get_table(element))

                    # Format the lists.
                    elif type == 'list':
                        # Loop over the list elements.
                        for j in range(len(element)):
                            text += "    - %s\n" % element[j]

                    # Format the item lists.
                    elif type == 'item list':
                        # Loop over the list elements.
                        for j in range(len(element)):
                            # No item.
                            if element[j][0] in [None, '']:
                                text += "    %s\n" % element[j][1]
                            else:
                                text += "    %s:  %s\n" % (element[j][0], element[j][1])

                    # The text object.
                    text_obj = wx.StaticText(panel, -1, text, style=wx.TE_MULTILINE)

                    # Format.
                    if type == 'title':
                        text_obj.SetFont(font.subtitle)
                    elif type == 'paragraph':
                        text_obj.SetFont(font.normal)
                    elif type in ['table', 'verbatim']:
                        text_obj.SetFont(font.modern_small)
                    else:
                        text_obj.SetFont(font.normal)

                    # Wrap the paragraphs and lists (with spacing for scrollbars).
                    if type in ['paragraph', 'list', 'item list']:
                        text_obj.Wrap(self._main_size - 20)

                    # The text size.
                    x, y = text_obj.GetSizeTuple()
                    tot_y += y

                    # The spacing after each element (except the last).
                    tot_y += spacing

                    # The spacing before each section (not including the first).
                    if i != 0 and type == 'title':
                        tot_y += spacing

                    # Append the text objects.
                    text_elements.append(text_obj)
                    text_types.append(type)

        # Some extra space for who knows what?!
        tot_y -= spacing
        tot_y += 20

        # Set the panel size - scrolling needed.
        if tot_y > max_y:
            panel.SetInitialSize((self._main_size, max_y))

        # Set the panel size - no scrolling.
        else:
            panel.SetInitialSize((self._main_size, tot_y))

        # Add the text.
        n = len(text_elements)
        for i in range(n):
            # Spacing before each section (not including the first).
            if i > 1 and text_types[i] == 'title':
                panel_sizer.AddSpacer(spacing)

            # The text.
            panel_sizer.Add(text_elements[i], 0, wx.ALIGN_LEFT, 0)

            # Spacer after all sections (except the end).
            if i != n - 1:
                panel_sizer.AddSpacer(spacing)

        # Set up and add the panel to the sizer.
        panel.SetSizer(panel_sizer)
        panel.SetAutoLayout(1)
        panel.SetupScrolling(scroll_x=False, scroll_y=True)
        sizer.Add(panel, 0, wx.ALL|wx.EXPAND)

        # A line with spacing.
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 0)
        sizer.AddSpacer(5)
