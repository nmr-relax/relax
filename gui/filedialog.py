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
"""relax specific file and directory dialogs."""

# Python module imports.
from os import chdir, getcwd
import wx

# relax module imports.
from status import Status; status = Status()

# relax GUI module imports.
from gui.misc import str_to_gui


def opendir(msg, default): # select directory, msg is message to display, default is starting directory
    newdir = None
    dlg = wx.DirDialog(None, message = msg, style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON, defaultPath = default)
    if dlg.ShowModal() == wx.ID_OK:
        newdir = dlg.GetPath()
        return newdir



class RelaxFileDialog(wx.FileDialog):
    """relax specific replacement file dialog for opening and closing files.

    This class provides the select() method so that this class can be used with a wx event.
    """

    def __init__(self, parent, field=None, message=wx.FileSelectorPromptStr, defaultDir=wx.EmptyString, defaultFile=wx.EmptyString, wildcard=wx.FileSelectorDefaultWildcardStr, style=wx.FD_DEFAULT_STYLE, pos=wx.DefaultPosition):
        """Setup the class and store the field.

        @param parent:          The parent wx window object.
        @type parent:           Window
        @keyword field:         The field to update with the file selection.
        @type field:            wx object or None
        @keyword message:       The file selector prompt string.
        @type message:          String
        @keyword defaultDir:    The directory to open in.
        @type defaultDir:       String
        @keyword defaultFile:   The file to default selection to.
        @type defaultFile:      String
        @keyword wildcard:      The file wildcard pattern.  For example for opening PDB files, this could be "PDB files (*.pdb)|*.pdb;*.PDB".
        @type wildcard:         String
        @keyword style:         The dialog style.  To open a single file, set to wx.FD_OPEN.  To open multiple files, set to wx.FD_OPEN|wx.FD_MULTIPLE.  To save a single file, set to wx.FD_SAVE.  To save multiple files, set to wx.FD_SAVE|wx.FD_MULTIPLE.
        @type style:            long
        @keyword pos:           The window position.
        @type pos:              Point
        """

        # Store the args.
        self.field = field
        self.style = style

        # No directory supplied, so use the current working directory.
        if defaultDir == wx.EmptyString:
            defaultDir = getcwd()

        # Initialise the base class.
        super(RelaxFileDialog, self).__init__(parent, message=message, defaultDir=defaultDir, defaultFile=defaultFile, wildcard=wildcard, style=style, pos=pos)


    def get_file(self):
        """Return the selected file.

        @return:        The name of the selected file(s).
        @rtype:         str or list of str
        """

        # The multiple files.
        if self.style in [wx.FD_OPEN|wx.FD_MULTIPLE, wx.FD_SAVE|wx.FD_MULTIPLE]:
            file = self.GetPaths()

        # The single file.
        else:
            file = self.GetPath()

        # Change the current working directory.
        chdir(self.GetDirectory())

        # Return the file.
        return file


    def select_event(self, event):
        """The file selector GUI element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Show the dialog, and return if nothing was selected.
        if status.show_gui and self.ShowModal() != wx.ID_OK:
            return

        # Get the selected file.
        file = self.get_file()

        # Update the field.
        self.field.SetValue(str_to_gui(file))

        # Scroll the text to the end.
        self.field.SetInsertionPoint(len(file))
