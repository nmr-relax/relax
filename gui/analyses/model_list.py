###############################################################################
#                                                                             #
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
"""Auto-analysis GUI element for the control of lists of models."""

# Python module imports.
import wx
import wx.lib.mixins.listctrl

# relax module imports.
from gui.fonts import font
from gui.message import Question
from gui.misc import add_border
from gui import paths
from gui.string_conv import list_to_gui, str_to_gui
from status import Status; status = Status()


class Model_list:
    """The model list GUI element."""

    # Class variables.
    desc = None
    """The short description for the GUI element."""

    models = []
    """The list of names of the model."""

    params = []
    """The list of parameters of each model in string form."""

    warning = None
    """A warning string which if set will present a warning message to the user prior to allowing them to modify the list of models."""

    red_flag = False
    """A flag which if True will cause the flag icon to turn red if the model list has been modified."""

    def __init__(self, parent, box):
        """Build the combo box list widget for a list of list selections.

        @param parent:      The parent GUI element.
        @type parent:       wx object instance
        @param box:         The sizer to put the combo box widget into.
        @type box:          wx.Sizer instance
        """

        # Store some args.
        self.parent = parent

        # Initialise all models as being selected.
        self.select = []
        for i in range(len(self.models)):
            self.select.append(True)

        # Initialise the model selection window.
        self.model_win = Model_sel_window(self.models, self.params)

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add a label.
        label = self.parent.add_static_text(sizer, self.parent, text=self.desc, width=self.parent.width_text)

        # Spacer.
        sizer.AddSpacer((self.parent.spacer_horizontal, -1))

        # The text input field.
        self.field = self.parent.add_text_control(sizer, self.parent, text=list_to_gui(self.GetValue()), editable=False)

        # Spacer.
        sizer.AddSpacer((self.parent.spacer_horizontal, -1))

        # Add the button.
        self.button = self.parent.add_button_open(sizer, self.parent, icon=paths.icon_16x16.flag_blue, text="Modify", fn=self.modify, width=self.parent.width_button, height=label.GetSize()[1]+8)

        # Add the contents to the main box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)


    def Enable(self, enable=True):
        """Enable or disable the element.

        @keyword enable:    The flag specifying if the element should be enabled or disabled.
        @type enable:       bool
        """

        # Call the control and button's method.
        self.field.Enable(enable)
        self.button.Enable(enable)


    def GetValue(self):
        """Return the list of models.

        @return:    The list of models.
        @rtype:     list of str
        """

        # Initialise.
        model_list = []

        # Add the models if they are selected.
        for i in range(len(self.models)):
            if self.select[i]:
                model_list.append(self.models[i])

        # Return the list.
        return model_list


    def set_value(self, value):
        """Store the list of models.

        @param value:   The list of models.
        @type value:    list of str
        """

        # First set all models as being deselected.
        for i in range(len(self.models)):
            self.select[i] = False

        # Select all models in the list.
        for model in value:
            # The model index.
            index = self.models.index(model)

            # Set the selected flag.
            self.select[index] = True

        # Update the button.
        self.update_button()

        # Update the GUI element.
        self.field.SetValue(list_to_gui(self.GetValue()))


    def modify(self, event=None):
        """Modify the model selection.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # First state that this should not be done.
        if self.warning and status.show_gui and not Question(self.warning, title="Warning - do not change!", size=(420, 210), default=False).ShowModal() == wx.ID_YES:
            return

        # Set the model selector window selections.
        self.model_win.set_selection(self.select)

        # Show the model selector window.
        if status.show_gui:
            self.model_win.ShowModal()
            self.model_win.Close()

        # Set the values.
        self.select = self.model_win.get_selection()

        # Update the button.
        self.update_button()

        # Update the GUI element.
        self.field.SetValue(list_to_gui(self.GetValue()))


    def update_button(self):
        """Update the button bitmap as needed."""

        # Nothing to do.
        if not self.red_flag:
            return

        # Change the flag to red to indicate to the user that changing the models is a bad thing!
        if False in self.select:
            self.button.SetBitmapLabel(wx.Bitmap(paths.icon_16x16.flag_red, wx.BITMAP_TYPE_ANY))

        # Otherwise set it to blue (in case all models are selected again).
        else:
            self.button.SetBitmapLabel(wx.Bitmap(paths.icon_16x16.flag_blue, wx.BITMAP_TYPE_ANY))



class Model_sel_window(wx.Dialog):
    """The model selector window object."""

    def __init__(self, models, params):
        """Set up the model selector window.

        @param models:  The list of models.
        @type models:   list of str
        @param params:  The list of parameters corresponding to the models.
        @type params:   list of str
        """

        # Set up the dialog.
        wx.Dialog.__init__(self, None, id=-1, title="Model list selector")

        # Initialise some values
        size_x = 500
        size_y = 300
        border = 10
        width = size_x - 2*border

        # Set the frame properties.
        self.SetSize((size_x, size_y))
        self.Centre()
        self.SetFont(font.normal)

        # The main box sizer.
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Pack the sizer into the frame.
        self.SetSizer(main_sizer)

        # Build the central sizer, with borders.
        sizer = add_border(main_sizer, border=border, packing=wx.VERTICAL)

        # Add a list control.
        self.model_list = ModelSelListCtrl(self)

        # The headers.
        self.model_list.InsertColumn(0, "Model")
        self.model_list.InsertColumn(1, "Parameters")

        # The widths.
        self.model_list.SetColumnWidth(0, int(0.4*width))
        self.model_list.SetColumnWidth(1, int(0.5*width))

        # Add the models and parameters.
        for i in range(len(models)):
            # Set the text.
            self.model_list.Append((str_to_gui(models[i]), str_to_gui(params[i])))

            # Set all selections to True.
            self.model_list.CheckItem(i)

        # Add the table to the sizer.
        sizer.Add(self.model_list, 1, wx.ALL|wx.EXPAND, 0)


    def get_selection(self):
        """Return the selection as a list of booleans.

        @return:    The list of models selected.
        @rtype:     list of bool
        """

        # Init.
        select = []

        # Loop over the entries.
        for i in range(self.model_list.GetItemCount()):
            select.append(self.model_list.IsChecked(i))

        # Return the list.
        return select


    def set_selection(self, select):
        """Set the selection.

        @param select:  The list of selections.
        @type select:   list of bool
        """

        # Loop over the entries.
        for i in range(self.model_list.GetItemCount()):
            self.model_list.CheckItem(i, check=select[i])



class ModelSelListCtrl(wx.ListCtrl, wx.lib.mixins.listctrl.CheckListCtrlMixin):
    """A special list control with checkboxes."""

    def __init__(self, parent):
        """Initialise the control.

        @param parent:  The parent window.
        @type parent:   wx.Frame instance
        """

        # Execute the list control __init__() method.
        wx.ListCtrl.__init__(self, parent, -1, style=wx.BORDER_SUNKEN|wx.LC_REPORT)

        # Execute the CheckListCtrlMixin __init__() method.
        wx.lib.mixins.listctrl.CheckListCtrlMixin.__init__(self)
